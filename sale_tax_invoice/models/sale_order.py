# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order.
        """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['invoice_type'] = self.invoice_type
        return invoice_vals