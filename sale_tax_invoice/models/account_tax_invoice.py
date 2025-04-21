# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountTaxInvoice(models.Model):
    _name = 'account.tax.invoice'
    _description = 'Tax Invoice Header'
    _order = 'invoice_date desc, doc_no desc'

    name = fields.Char(string="Reference", related='doc_no', store=True, index=True) # For display name
    doc_no = fields.Char(
        string='Document No.', required=True, copy=False, readonly=True, index=True,
        default=lambda self: _('New'))

    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True, index=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_name = fields.Char(string="Partner Name", related='partner_id.display_name', store=True)
    partner_tax_id = fields.Char(string="Partner Tax ID", related='partner_id.vat', store=True)

    so_date = fields.Date(string='Sale Order Date', readonly=True)
    invoice_date = fields.Date(string='Invoice Date', required=True, index=True, readonly=True)
    invoice_month = fields.Char(string='Invoice Month (YYYY-mm)', compute='_compute_invoice_month', store=True, index=True)

    sum_amount_line_vat = fields.Monetary(string='Total Line Amount (VAT)', compute='_compute_amounts', store=True)
    sum_amount_line_non_vat = fields.Monetary(string='Total Line Amount (Non-VAT)', compute='_compute_amounts', store=True)
    sum_amount_vat = fields.Monetary(string='Total VAT Amount', compute='_compute_amounts', store=True)
    sum_total = fields.Monetary(string='Subtotal (VAT Lines + VAT)', compute='_compute_amounts', store=True)
    sum_net_price = fields.Monetary(string='Net Total', compute='_compute_amounts', store=True)

    sale_order_id = fields.Many2one('sale.order', string='Source Sale Order', readonly=True)
    invoice_id = fields.Many2one(
        'account.move', string='Source Invoice', required=True, ondelete='cascade', index=True, readonly=True)

    tax_invoice_level = fields.Selection(
        [('summary', 'Summary'), ('line', 'Line')],
        string='Tax Invoice Level', required=True, readonly=True)

    line_ids = fields.One2many('account.tax.invoice.line', 'account_tax_invoice_id', string='Tax Invoice Lines')

    company_id = fields.Many2one('res.company', string='Company', related='invoice_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='invoice_id.currency_id', store=True, readonly=True)

    @api.depends('invoice_date')
    def _compute_invoice_month(self):
        for record in self:
            if record.invoice_date:
                record.invoice_month = record.invoice_date.strftime('%Y-%m')
            else:
                record.invoice_month = False

    @api.depends('line_ids.amount_line_vat', 'line_ids.amount_line_non_vat', 'line_ids.amount_vat')
    def _compute_amounts(self):
        """ Compute the sums from the lines. """
        for record in self:
            record.sum_amount_line_vat = sum(record.line_ids.mapped('amount_line_vat'))
            record.sum_amount_line_non_vat = sum(record.line_ids.mapped('amount_line_non_vat'))
            record.sum_amount_vat = sum(record.line_ids.mapped('amount_vat'))
            record.sum_total = record.sum_amount_line_vat + record.sum_amount_vat
            record.sum_net_price = record.sum_total + record.sum_amount_line_non_vat

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('doc_no', _('New')) == _('New'):
                seq_date = fields.Date.context_today(self)
                # Determine Prefix based on invoice type or other logic if needed
                prefix_code = 'account.tax.invoice.sequence' # Use one sequence for now
                if vals.get('invoice_type') == 'TINV': prefix_code = 'account.tax.invoice.sequence'
                vals['doc_no'] = self.env['ir.sequence'].next_by_code(prefix_code, sequence_date=seq_date) or _('New')
        return super().create(vals_list)