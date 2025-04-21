from odoo import _, models, fields
from .common import STD_COST_CALCULATION_TYPES

class StandardCostInherit(models.Model):
    _inherit = 'product.template'
 
    std_cost = fields.Float(string='Standard Cost', default=0.0)
    std_cost_cal_type = fields.Selection(
        selection=STD_COST_CALCULATION_TYPES,
        string=_('Standard Cost Calculate Type'),
        default='0'
    )
    std_cost_cal_val = fields.Float('Standard Cost Calculate Value')
    std_cost_history_ids = fields.One2many('product.standard.cost.history', 'product_tmpl_id', string='Standard Cost History')
    
    def action_view_std_cost_history(self):
        self.ensure_one()
        return {
            'name': 'Standard Cost History',
            'type': 'ir.actions.act_window',
            'res_model': 'product.standard.cost.history',
            'domain': [('product_tmpl_id', '=', self.id)],
            'view_mode': 'tree,form',
            'context': {'default_product_tmpl_id': self.id},
        }