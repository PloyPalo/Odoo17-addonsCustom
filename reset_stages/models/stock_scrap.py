from odoo import models, _

class StockScrap(models.Model):
    _inherit = 'stock.scrap'
    
    def action_reset_to_draft(self):
        for scrap in self:
            if scrap.state != 'done':
                continue
            # ตรวจสอบการเคลื่อนย้ายสินค้าที่เกี่ยวข้อง
            if scrap.move_ids and scrap.move_ids.state == 'done':
                # กลับรายการเคลื่อนย้ายสต็อก
                scrap.move_ids._action_cancel()
                scrap.move_ids.sudo().write({'state': 'draft'})
            
            # เปลี่ยนสถานะเป็น draft
            scrap.write({'state': 'draft'})
        
        return True