from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    std_cost = fields.Float(
        related='product_id.std_cost',
        string='Standard Cost',
        readonly=True,
        store=True
    )
                
    final_std_cost = fields.Float(
        string='Final Standard Cost',
        compute='_compute_final_std_cost',
        store=True
    )
    
    @api.depends('std_cost', 'product_uom_qty', 'product_id.standard_price', 'order_id.company_id.standard_cost_rate')
    def _compute_final_std_cost(self):
        for line in self:
            if line.std_cost:
                base_std_cost = line.std_cost
            else:
                standard_cost_rate = line.order_id.company_id.standard_cost_rate
                base_std_cost = line.product_id.standard_price * (1 + standard_cost_rate)
                line.std_cost = base_std_cost
            
            line.final_std_cost = base_std_cost * line.product_uom_qty
    