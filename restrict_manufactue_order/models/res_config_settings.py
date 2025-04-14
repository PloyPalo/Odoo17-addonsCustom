from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custom_feature_restrict_mo = fields.Boolean(
        string='Restricted Manufacturing Order',
        config_parameter='restrict_manufactue_order.enable_stock_validation',
        help='Enable validation of available stock before confirming manufacturing orders'
    )