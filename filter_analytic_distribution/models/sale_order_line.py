from odoo import api, fields, models

class SaleOrderLine(models.Model):
    """Extends sales order lines to manage analytic account distribution.
    This enhancement automatically sets analytic account allocations based on
    the analytic projects linked to the parent sales order when a product is
    selected.
    """

    _inherit = 'sale.order.line'

    @api.depends('product_template_id')
    @api.onchange('product_template_id')
    def _compute_analytic_distribution(self):
        """Compute analytic account distribution based on order's analytic projects.

        Behavior:
        - When analytic projects exist on the sales order:
          * Collects all linked analytic accounts from projects
          * Allocates 100% to each associated analytic account
        - When no analytic projects exist:
          * Clears existing distribution

        Notes:
        - Percentage allocation is fixed at 100% per analytic account
        - Overwrites any existing manual distribution on product selection
        """
        for line in self:
            if line.order_id.analytic_project_ids:
                analytic_ids = line.order_id.analytic_project_ids._origin.mapped('analytic_account_id').ids
                line.analytic_distribution = {
                    analytic_id: 100
                    for analytic_id in analytic_ids
                }
            else:
                line.analytic_distribution = {}