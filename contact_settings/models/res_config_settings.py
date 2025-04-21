from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    no_space_title_name = fields.Boolean(
        related="company_id.no_space_title_name", readonly=False
    )
    
    partner_names_order = fields.Selection(
        [('first_last', 'Firstname Lastname'),
         ('last_first', 'Lastname Firstname')],
        string='Partner Names Order',
        config_parameter='partner_firstname.order')