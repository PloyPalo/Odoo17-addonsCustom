from odoo import fields, models


class SaleOrderInherit(models.Model):
    """
        This model extends 'sale.order' to include a many-to-many relationship
        with projects and provides a method to compute related analytic accounts.
        """
    _inherit = 'sale.order'

    analytic_project_ids = fields.Many2many('project.project',
                                            help="Projects associated with this sale order.",
                                            string='Projects')

    def compute_analytic_account(self):
        """
           Computes and returns the IDs of analytic accounts linked to the selected projects.
           :return: List of analytic account IDs.
           :rtype: list
               """
        return self.analytic_project_ids.mapped('analytic_account_id').ids
