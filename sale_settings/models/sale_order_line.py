from odoo import models, fields, api

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    type = fields.Char(string="Type", required=False)
