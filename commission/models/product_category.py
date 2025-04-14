from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    product_commission = fields.Float(
        string='Product Commission',
        default=0.0,
        digits=(5,2)
    )