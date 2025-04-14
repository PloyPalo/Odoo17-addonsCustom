from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    sale_line_product_type = fields.Char(
        string="Type",
        compute='_compute_sale_line_type',
        store=True
    )

    sale_line_ids = fields.Many2many(
        'sale.order.line',
        'sale_order_line_invoice_rel',
        'invoice_line_id',
        'order_line_id',
        string='Sale Order Lines',
        readonly=True
    )

    @api.depends('sale_line_ids')  
    def _compute_sale_line_type(self): 
        for rec in self:
            sale_line = rec.sale_line_ids[:1] 
            rec.sale_line_product_type = sale_line.type if sale_line else False

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    note = fields.Char(string="Note", required=False)