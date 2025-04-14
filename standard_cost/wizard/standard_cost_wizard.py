from odoo import models, fields, api

class StandardCostWizard(models.TransientModel):
    _name = 'standard.cost.wizard'
    _description = 'Standard Cost Calculator'

    product_id = fields.Many2one('product.product', string='Product Variant', required=True, ondelete='cascade')
    standard_price = fields.Float(related='product_id.standard_price', string='Cost', readonly=True)
    std_cost_cal_type = fields.Selection([
        ('0', 'Percentage'),
        ('1', 'Fixed'),
    ], string='Standard Cost Calculate Type', required=True, default='0')
    std_cost = fields.Float('Standard Cost', required=True, default=0)
    std_cost_cal_value = fields.Float('Standard Cost Calculate Value', required=True, default=0)
    calculated_preview = fields.Float('Calculated Result', compute='_compute_calculation', store=False)
    
    @api.model
    def default_get(self, fields):
        res = super(StandardCostWizard, self).default_get(fields)
        if self._context.get('active_id'):
            product_tmpl = self.env['product.template'].browse(self._context.get('active_id'))
            product = product_tmpl.product_variant_id
            if product:
                res.update({
                    'product_id': product.id,
                    'std_cost_cal_type': product.std_cost_cal_type,
                    'std_cost_cal_value': product.std_cost_cal_val,
                })
        return res

    @api.depends('std_cost_cal_type', 'std_cost_cal_value', 'standard_price')
    def _compute_calculation(self):
        for record in self:
            if record.std_cost_cal_type == '0':  # Percentage
                record.calculated_preview = record.standard_price + (record.standard_price * record.std_cost_cal_value / 100)
            else:  # Fixed Bath
                record.calculated_preview = record.std_cost_cal_value

    def action_save(self):
        self.ensure_one()
        if self.std_cost_cal_type == '0':  # Percentage
            calculated_cost = self.standard_price + (self.standard_price * self.std_cost_cal_value / 100)
        else:  # Fixed Bath
            calculated_cost = self.std_cost_cal_value
        
        self.product_id.write({
            'std_cost': calculated_cost,  # เก็บราคาที่คำนวณแล้วในฟิลด์แยก
            'std_cost_cal_type': self.std_cost_cal_type,
            'std_cost_cal_val': self.std_cost_cal_value,
        })
        return {'type': 'ir.actions.act_window_close'}