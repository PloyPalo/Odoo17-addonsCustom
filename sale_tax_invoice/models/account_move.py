# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_type = fields.Selection(
        [
            ("invoice", "Invoice"),
            ("tax_invoice", "Tax Invoice"),
        ],
        string="Invoice Type",
        readonly=True,
        copy=False,
        states={"draft": [("readonly", False)]},
    )

    # Link to the generated tax invoice record(s)
    tax_invoice_ids = fields.One2many(
        "account.tax.invoice", "invoice_id", string="Tax Invoices", copy=False
    )
    tax_invoice_count = fields.Integer(
        compute="_compute_tax_invoice_count", string="Tax Invoice Count"
    )

    @api.depends("tax_invoice_ids")
    def _compute_tax_invoice_count(self):
        for move in self:
            move.tax_invoice_count = len(move.tax_invoice_ids)

    # 3. Functionality: Trigger on Invoice Confirmation (Post)
    def action_post(self):
        """Override to create tax invoice data"""
        res = super(AccountMove, self).action_post()
        for move in self:
            # Only process Customer Invoices/Credit Notes originating from SO
            if move.move_type in ("out_invoice", "out_refund") and move.invoice_origin:
                # Prevent duplicate creation if re-posting
                if not move.tax_invoice_ids:
                    try:
                        move._create_tax_invoice_data()
                    except Exception as e:
                        _logger.error(
                            f"Failed to create tax invoice data for {move.name}: {e}",
                            exc_info=True,
                        )
                        # Optional: Raise UserError to block posting if tax data is critical
                        # raise UserError(_("Failed to generate Tax Invoice data. Error: %s") % e)
        return res

    def _get_tax_invoice_setting(self):
        """Helper to get the configuration setting"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("tax_invoice.default_tax_invoice_level", "line")
        )

    def _find_source_sale_order(self):
        """Attempt to find the related Sale Order"""
        self.ensure_one()
        if self.invoice_origin:
            # Basic search by name - might need refinement for complex cases
            so = self.env["sale.order"].search(
                [("name", "=", self.invoice_origin)], limit=1
            )
            return so
        # Fallback: Check linked sale order lines if invoice_origin is missing/unreliable
        # This requires sale_subscription or similar modules linking SO lines to Inv lines
        # so_ids = self.invoice_line_ids.mapped('sale_line_ids.order_id')
        # if len(so_ids) == 1:
        #     return so_ids
        return self.env["sale.order"]  # Return empty recordset if not found

    def _create_tax_invoice_data(self):
        """Creates the account.tax.invoice and line records"""
        self.ensure_one()
        TaxInvoice = self.env["account.tax.invoice"]
        TaxInvoiceLine = self.env["account.tax.invoice.line"]
        config_type = self._get_tax_invoice_setting()
        source_so = self._find_source_sale_order()

        # Prepare Header Vals
        header_vals = {
            "partner_id": self.partner_id.id,
            "so_date": source_so.date_order if source_so else None,
            "invoice_date": self.invoice_date or fields.Date.context_today(self),
            "sale_order_id": source_so.id if source_so else None,
            "invoice_id": self.id,
            "tax_invoice_level": config_type,
            "company_id": self.company_id.id,
            # doc_no is generated on create
        }

        # Prepare Line Vals (calculation logic)
        line_vals_list = []
        summary_data = {
            "amount_line_vat": 0.0,
            "amount_line_non_vat": 0.0,
            "amount_vat": 0.0,
        }

        product_lines = self.invoice_line_ids.filtered(
            lambda l: l.display_type == False or l.display_type == "product"
        )
        # Exclude zero quantity lines unless specifically needed (e.g., free items)
        # product_lines = product_lines.filtered(lambda l: l.quantity != 0)

        for line in product_lines:
            # Distinguish based on taxes applied
            has_vat = any(
                tax.amount != 0 for tax in line.tax_ids
            )  # Simple check: any non-zero tax is VAT related
            line_subtotal_before_discount = line.price_unit * line.quantity
            discount_amount = line_subtotal_before_discount * (line.discount / 100.0)
            line_subtotal = (
                line_subtotal_before_discount - discount_amount
            )  # Price * Qty - Discount

            # VAT amount calculation relies on Odoo's computation stored in price_total/price_subtotal
            # price_subtotal is amount BEFORE tax, price_total is amount AFTER tax
            # This works even with complex tax setups (e.g., tax included in price)
            line_vat_amount = line.price_total - line.price_subtotal

            line_data = {
                "amount_line_vat": 0.0,
                "amount_line_non_vat": 0.0,
                "amount_vat": 0.0,
                "invoice_line_id": line.id,  # Needed for 'line' type
            }

            if has_vat:
                # Note: line.price_subtotal *is* the base amount for VAT calculation
                line_data["amount_line_vat"] = (
                    line.price_subtotal
                )  # Base amount before VAT
                line_data["amount_vat"] = line_vat_amount
                summary_data["amount_line_vat"] += line.price_subtotal
                summary_data["amount_vat"] += line_vat_amount
            else:
                # If no VAT, the line amount contributes to non-VAT sum
                line_data["amount_line_non_vat"] = (
                    line.price_subtotal
                )  # Subtotal IS the non-vat amount here
                summary_data["amount_line_non_vat"] += line.price_subtotal

            if config_type == "line":
                # Calculate derived fields for the line record directly
                line_total = line_data["amount_line_vat"] + line_data["amount_vat"]
                line_net_price = line_total + line_data["amount_line_non_vat"]
                line_vals_list.append(
                    (
                        0,
                        0,
                        {
                            **line_data  # Spread the calculated amounts
                            # 'total': line_total, # Computed fields will calculate these
                            # 'net_price': line_net_price, # Computed fields will calculate these
                        },
                    )
                )

        if config_type == "summary":
            # Calculate derived fields for the summary record directly
            summary_total = summary_data["amount_line_vat"] + summary_data["amount_vat"]
            summary_net_price = summary_total + summary_data["amount_line_non_vat"]
            line_vals_list.append(
                (
                    0,
                    0,
                    {
                        "amount_line_vat": summary_data["amount_line_vat"],
                        "amount_line_non_vat": summary_data["amount_line_non_vat"],
                        "amount_vat": summary_data["amount_vat"],
                        # 'total': summary_total, # Computed fields will calculate these
                        # 'net_price': summary_net_price, # Computed fields will calculate these
                        "invoice_line_id": None,  # No specific line for summary
                    },
                )
            )

        # Add lines to header vals
        header_vals["line_ids"] = line_vals_list

        # Create the Tax Invoice record
        _logger.info(
            f"Creating tax invoice data for invoice {self.name} with type '{config_type}'. Header: {header_vals}"
        )
        new_tax_invoice = TaxInvoice.create(header_vals)
        _logger.info(
            f"Successfully created tax invoice {new_tax_invoice.doc_no} (ID: {new_tax_invoice.id}) for invoice {self.name}"
        )

        return new_tax_invoice

    # Action Button to view related tax invoices
    def action_view_tax_invoices(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "tax_invoice.action_account_tax_invoice"
        )
        if self.tax_invoice_count == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.tax_invoice_ids[0].id,
                    "views": [(False, "form")],
                }
            )
        else:
            action["domain"] = [("id", "in", self.tax_invoice_ids.ids)]
        action["context"] = dict(
            self._context, create=False
        )  # Prevent creation from this view
        return action
