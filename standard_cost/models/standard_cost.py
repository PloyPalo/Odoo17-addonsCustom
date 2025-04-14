from odoo import models, fields, api

class StandardCostInherit(models.Model):
    _inherit = 'product.template'
 
    std_cost = fields.Float(string='Standard Cost', default=0.0)
    std_cost_cal_type = fields.Selection([
        ('0', 'Percentage'),
        ('1', 'Fixed'),
    ], string='Standard Cost Calculate Type', default='0')
    std_cost_cal_val = fields.Float('Standard Cost Calculate Value')