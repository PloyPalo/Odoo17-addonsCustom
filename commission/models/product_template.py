from odoo import models,fields, api
from odoo.exceptions import ValidationError

class ProductInherit(models.Model):
    _inherit = 'product.template'

    category_commission = fields.Float(
        string='Category Commission',
        compute='_compute_category_commission',
        store=True
    )

    @api.depends('categ_id', 'categ_id.product_commission')
    def _compute_category_commission(self):
        for product in self:
            product.category_commission = product.categ_id.product_commission