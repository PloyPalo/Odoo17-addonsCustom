from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    standard_cost_rate = fields.Float(
        related='company_id.standard_cost_rate',
        readonly=False,
        string='Standard Cost Rate (%)',
        help='Default percentage rate for calculating standard cost in sales orders',
        config_parameter='company.standard_cost_rate'
    )