from odoo import _, models, fields, api
from .common import STD_COST_CALCULATION_TYPES

class StandardCostHistory(models.Model):
    _name = 'product.standard.cost.history'
    _description = 'Product Standard Cost History'
    _order = 'date_updated DESC'
    
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', required=True, ondelete='cascade')
    std_cost = fields.Float(string='Standard Cost', required=True)
    date_updated = fields.Datetime(string='Update Date', default=fields.Datetime.now, required=True)
    std_cost_cal_type = fields.Selection(
        selection=STD_COST_CALCULATION_TYPES,
        string=_('Standard Cost Calculate Type')
    )
    std_cost_cal_val = fields.Float('Calculation Value')
    is_latest_record = fields.Boolean(compute='_compute_is_latest_record', store=False)
    
    # เพิ่มฟิลด์สำหรับเก็บข้อมูลผู้สร้างและแก้ไข
    create_uid = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user.id, readonly=True)
    create_date = fields.Datetime('Created on', default=lambda self: fields.Datetime.now(), readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Updated by', readonly=True)
    write_date = fields.Datetime('Last Updated on', readonly=True)
    
    @api.depends('date_updated')
    def _compute_is_latest_record(self):
        for record in self:
            latest_record = self.search([
                ('product_tmpl_id', '=', record.product_tmpl_id.id)
            ], order='date_updated DESC', limit=1)
            record.is_latest_record = (record.id == latest_record.id)
    
    def action_choose_value(self):
        self.ensure_one()
        # เมื่อกดปุ่ม "Choose" จะเปิด wizard พร้อมกับข้อมูล std cost ที่เลือก
        return {
            'name': 'Calculate Standard Cost',
            'type': 'ir.actions.act_window',
            'res_model': 'standard.cost.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_tmpl_id': self.product_tmpl_id.id,
                'default_std_cost_cal_type': self.std_cost_cal_type,
                'default_std_cost_cal_value': self.std_cost_cal_val,
                'default_history_value': self.std_cost,
            },
        }