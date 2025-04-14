from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = "res.company"

    # Define fields first
    branch = fields.Char(
        string="Tax Branch",
        copy=False,
        store=True,
        help="Branch ID, e.g., 0000, 0001, ...",
    )
    no_space_title_name = fields.Boolean(
        string="No Space Title and Name",
        help="If checked, title and name will no space",
    )

    # Then define methods
    def write(self, vals):
        res = super().write(vals)
        if "no_space_title_name" in vals:
            personal_partners = (
                self.env["res.partner"]
                .search([("title", "!=", False)])
                .with_context(skip_inverse_name=True)
            )
            for partner in personal_partners:
                partner.name = partner._get_computed_name(
                    partner.lastname, partner.firstname
                )
        return res