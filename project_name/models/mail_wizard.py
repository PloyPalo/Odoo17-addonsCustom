from odoo import models, fields, api

class MailWizardInvite(models.TransientModel):
    _inherit = 'mail.wizard.invite'
    
    department_id = fields.Many2one('project.department', string='Department')
    
    @api.onchange('department_id')
    def _onchange_department_id(self):
        """เมื่อเลือกแผนก ให้ดึงข้อมูลสมาชิกในแผนกให้อัตโนมัติ"""
        if self.department_id and self.department_id.member_ids:
            self.partner_ids = [(6, 0, self.department_id.member_ids.ids)]
        else:
            self.partner_ids = [(5, 0, 0)]  # ล้างค่า partner_ids ถ้าไม่ได้เลือกแผนก