from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    standard_cost_rate = fields.Float(
        string='Standard Cost Rate (%)',
        default=0.0
    )