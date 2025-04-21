from odoo import models, api, _

class SaleOrderCancel(models.TransientModel):
    _inherit = 'sale.order.cancel'
    
    def action_cancel(self):
        """
        Override the action_cancel method of the wizard to delete stock.picking records
        before calling the original method if the setting is enabled
        """
        # ดึงข้อมูล sale order จาก context
        sale_order_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(sale_order_id)
        
        deleted_count = 0
        
        # ตรวจสอบการตั้งค่าจาก config_parameter
        delete_pickings = self.env['ir.config_parameter'].sudo().get_param(
            'sale_picking_cleanup.delete_draft_pickings', 'False').lower() == 'true'
            
        if delete_pickings:
            # ค้นหาและลบ stock.picking ที่เกี่ยวข้อง
            pickings_to_delete = self.env['stock.picking'].search([
                ('sale_id', '=', sale_order_id),
                ('state', 'in', ['draft', 'waiting', 'confirmed', 'cancel'])
            ])
            
            deleted_count = len(pickings_to_delete)
            if pickings_to_delete:
                pickings_to_delete.unlink()
        
        # เรียกฟังก์ชัน action_cancel เดิม
        result = super(SaleOrderCancel, self).action_cancel()
            
        # แสดงข้อความแจ้งเตือนและตั้งค่า timeout ก่อนรีเฟรช
        if deleted_count > 0:
            msg = _("%d stock transfer(s) have been deleted.") % deleted_count
            # สร้าง notification แล้วใส่ timeout ให้รีเฟรชหลังแสดงข้อความ 2 วินาที
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Stock Transfers Deleted'),
                    'message': msg,
                    'type': '',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},  # ปิด wizard ก่อน
                    'duration': 250,  # แสดงครึ่งวินาที
                },
                'close_all_notifications': True
            }
        
        return result

    # เพิ่มฟังก์ชันสำหรับให้มีการรีเฟรชหลังจากแสดงข้อความ
    def action_cancel_and_refresh(self):
        """
        Action to handle notification and refresh
        """
        # เรียกฟังก์ชัน action_cancel ก่อน
        notification_result = self.action_cancel()
        
        # สร้าง chain actions เพื่อให้รีเฟรชหลังแสดงข้อความ
        return {
            'type': 'ir.actions.act_window_close',
            'followup': notification_result,
            'followup_type': 'reload',
        }