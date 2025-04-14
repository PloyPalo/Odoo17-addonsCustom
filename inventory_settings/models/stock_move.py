from odoo import models, fields, api

class StockMoveInherit(models.Model):
    _inherit = 'stock.move'
    
    type = fields.Char(
        string="Type",
        related='sale_line_id.type',
        store=True,
        readonly=True
    )

class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'
    
    stock_move_product_type = fields.Char(
        string="Type",
        related='move_id.type',
        store=True,
        readonly=True
    )

class StockValuationLayerInherit(models.Model):
    _inherit = 'stock.valuation.layer'

    product_type = fields.Char(
        string="Type",
        related='stock_move_id.type',
        store=True,
        readonly=True
    )
