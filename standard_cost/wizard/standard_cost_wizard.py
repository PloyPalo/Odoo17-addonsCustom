from odoo import _, models, fields, api
from ..models.common import STD_COST_CALCULATION_TYPES

class StandardCostWizard(models.TransientModel):
    _name = 'standard.cost.wizard'
    _description = 'Standard Cost Calculator'

    product_id = fields.Many2one('product.product', string='Product Variant', required=True, ondelete='cascade')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    standard_price = fields.Float(related='product_id.standard_price', string='Cost', readonly=True)
    std_cost_cal_type = fields.Selection(
        selection=STD_COST_CALCULATION_TYPES,
        string=_('Standard Cost Calculate Type'),
        required=True, 
        default='0'
    )
    std_cost = fields.Float('Standard Cost', required=True, default=0)
    std_cost_cal_value = fields.Float('Standard Cost Calculate Value', required=True, default=0)
    calculated_preview = fields.Float('Calculated Result', compute='_compute_calculation', store=False)
    history_value = fields.Float('History Value', default=0.0)
    
    @api.model
    def default_get(self, fields):
        res = super(StandardCostWizard, self).default_get(fields)
        
        # ตรวจสอบว่ามีการส่งค่า history_value มาหรือไม่
        if self._context.get('default_history_value'):
            res['history_value'] = self._context.get('default_history_value')
            
        # ตรวจสอบว่ามีการส่งค่า product_tmpl_id มาหรือไม่
        if self._context.get('default_product_tmpl_id'):
            product_tmpl = self.env['product.template'].browse(self._context.get('default_product_tmpl_id'))
            if product_tmpl.exists():
                res['product_tmpl_id'] = product_tmpl.id
                # กรณีที่มีเพียง variant เดียว
                if product_tmpl.product_variant_id:
                    res['product_id'] = product_tmpl.product_variant_id.id
        
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
        
        # Update the product template
        product_tmpl = self.product_tmpl_id or self.product_id.product_tmpl_id
        product_tmpl.write({
            'std_cost': calculated_cost,
            'std_cost_cal_type': self.std_cost_cal_type,
            'std_cost_cal_val': self.std_cost_cal_value,
        })
        
        # Create a history record
        self.env['product.standard.cost.history'].create({
            'product_tmpl_id': product_tmpl.id,
            'std_cost': calculated_cost,
            'std_cost_cal_type': self.std_cost_cal_type,
            'std_cost_cal_val': self.std_cost_cal_value,
        })
        
        return {'type': 'ir.actions.act_window_close'}