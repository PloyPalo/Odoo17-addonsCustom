from odoo import models, api, fields, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'
    
    # ฟิลด์ที่อนุญาตให้แก้ไขได้
    ALLOWED_FIELDS = [
        # Chatter fields
        'message_follower_ids', 'message_ids', 'message_main_attachment_id',
        'message_attachment_count', 'message_unread', 'message_unread_counter',
        
        # Activity fields
        'activity_ids', 'activity_state', 'activity_user_id', 
        'activity_type_id', 'activity_date_deadline', 
        'activity_summary', 'activity_exception_decoration'
    ]
    
    def write(self, vals):
        """
        Override write method to prevent modifications except for chatter and activity fields
        """
        # ค้นหากลุ่ม Design Manager Group
        design_manager_group = self.env['res.groups'].search([('name', '=', 'Design Manager Group')])
        
        # ตรวจสอบว่าผู้ใช้อยู่ในกลุ่ม Design Manager Group
        if design_manager_group and design_manager_group in self.env.user.groups_id:
            # ตรวจสอบฟิลด์ที่กำลังจะแก้ไข
            for key in list(vals.keys()):
                # หากฟิลด์ไม่อยู่ในรายการที่อนุญาต ให้ raise AccessError
                if key not in self.ALLOWED_FIELDS:
                    _logger.warning(f"Blocking modification of field: {key} by Design Manager")
                    raise AccessError(_(f"คุณไม่สามารถแก้ไขฟิลด์: {key} ได้"))
        
        return super(Project, self).write(vals)