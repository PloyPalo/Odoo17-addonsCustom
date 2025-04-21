# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountTaxInvoiceLine(models.Model):
    _name = 'account.tax.invoice.line'
    _description = 'Tax Invoice Line Detail'

    account_tax_invoice_id = fields.Many2one(
        'account.tax.invoice', string='Tax Invoice Header', required=True, ondelete='cascade', index=True)

    amount_line_vat = fields.Monetary(string='Line Amount (VAT)')
    amount_line_non_vat = fields.Monetary(string='Line Amount (Non-VAT)')
    amount_vat = fields.Monetary(string='VAT Amount')
    total = fields.Monetary(string='Subtotal', compute='_compute_total', store=True)
    net_price = fields.Monetary(string='Net Price', compute='_compute_net_price', store=True)

    invoice_line_id = fields.Many2one('account.move.line', string='Source Invoice Line', ondelete='set null') # Allow null for summary

    # Currency helper
    currency_id = fields.Many2one(related='account_tax_invoice_id.currency_id', store=True, string='Currency')
    company_id = fields.Many2one(related='account_tax_invoice_id.company_id', store=True, string='Company')

    @api.depends('amount_line_vat', 'amount_vat')
    def _compute_total(self):
        for line in self:
            line.total = line.amount_line_vat + line.amount_vat

    @api.depends('total', 'amount_line_non_vat')
    def _compute_net_price(self):
        for line in self:
            line.net_price = line.total + line.amount_line_non_vat