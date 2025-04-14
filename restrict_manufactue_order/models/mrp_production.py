from odoo import models, _
from odoo.exceptions import ValidationError

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        # Check if validation is enabled in settings
        enable_validation = self.env['ir.config_parameter'].sudo().get_param(
            'restrict_manufactue_order.enable_stock_validation', False)
        
        if enable_validation:
            insufficient_products = self.move_raw_ids.filtered(
                lambda m: m.product_id.qty_available < m.product_uom_qty)
            if insufficient_products:
                error_message = "\n".join(
                    f"{move.product_id.display_name}: Available ({move.product_id.qty_available}), "
                    f"Required ({move.product_uom_qty})"
                    for move in insufficient_products
                )
                raise ValidationError(
                    f"The following products have insufficient stock:\n{error_message}")
        
        return super().action_confirm()