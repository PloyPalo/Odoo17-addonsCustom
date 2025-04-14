from odoo import models,fields, api
from odoo.exceptions import ValidationError

class ProductInherit(models.Model):
    _inherit = 'product.template'
    
    product_external_code = fields.Char(string='Product External Code', required=False, trim=True) # Auto-trim spaces at start/end
    product_internal_code = fields.Char(string='Product Internal Code', required=False, trim=True) # Auto-trim spaces at start/end
    sale_ok = fields.Boolean(default=True)
    purchase_ok = fields.Boolean(default=True)
    can_be_expensed = fields.Boolean(default=True)
    
    @api.onchange('product_external_code', 'product_internal_code')
    def _onchange_product_codes(self):
        if self.product_external_code:
            self.product_external_code = self.product_external_code.replace(' ', '')
        if self.product_internal_code:
            self.product_internal_code = self.product_internal_code.replace(' ', '')