from odoo import fields, models

class ResPartnerCompanyType(models.Model):
    _inherit = "res.partner.company.type"

    prefix = fields.Char(translate=True)
    suffix = fields.Char(translate=True)
    use_prefix_suffix = fields.Boolean(
        default=True,
        help="Enable prefix and suffix in company name",
    )