from odoo import models, fields, api
from odoo.tools.translate import _

class SaleOrderTaxConfirmation(models.TransientModel):
    _name = 'sale.order.tax.confirmation'
    _description = 'Sale Order Tax Confirmation'
    
    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    has_mixed_products = fields.Boolean(string='Mixed Products (Goods/Service)')
    has_mixed_tax_scopes = fields.Boolean(string='Mixed Tax Scopes (Goods/Service)')
    has_missing_force_tax = fields.Boolean(string='Missing Force Tax')
    force_tax_id = fields.Many2one('account.tax', string='Force Tax Invoice', domain=[('force_tax_invoice', '=', True)])
    
    @api.model
    def default_get(self, fields):
        """
        Override default_get กำหนดค่าเริ่มต้นสำหรับ force_tax_id และตรวจสอบสถานะของ order
        """
        res = super(SaleOrderTaxConfirmation, self).default_get(fields)
        
        # ดึงข้อมูลจาก context
        order_id = self._context.get('active_id')
        if order_id:
            order = self.env['sale.order'].browse(order_id)
            res['order_id'] = order.id
            
            # ตรวจสอบการผสมกันของประเภทสินค้าและประเภทภาษี
            product_types = set()
            tax_scopes = set()
            
            for line in order.order_line:
                if line.product_id:
                    product_types.add(line.product_id.type)
                    for tax in line.tax_id:
                        tax_scopes.add(tax.tax_scope)
            
            # กำหนดค่าตามผลการตรวจสอบ
            res['has_mixed_products'] = len(product_types) > 1
            res['has_mixed_tax_scopes'] = len(tax_scopes) > 1
        
        # ถ้าไม่มี force_tax_id ให้ค้นหาภาษีที่ถูกกำหนดให้เป็น force_tax_invoice
        if 'force_tax_id' not in res or not res['force_tax_id']:
            force_tax = self.env['account.tax'].search([('force_tax_invoice', '=', True)], limit=1)
            if force_tax:
                res['force_tax_id'] = force_tax.id
            
        return res
    
    def action_confirm(self):
        """
        ดำเนินการยืนยันการปรับภาษีและยืนยันคำสั่งซื้อ
        """
        self.ensure_one()
        order = self.order_id
        
        # ตรวจสอบว่ามีการเลือกภาษีหรือไม่
        if not self.force_tax_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('คำเตือน!'),
                    'message': _('กรุณาเลือกภาษีที่ต้องการใช้ก่อนดำเนินการต่อ'),
                    'type': 'warning',
                    'sticky': True,
                }
            }
        
        # ทำการปรับภาษีทุกรายการให้เป็นภาษีที่เลือก
        for line in order.order_line:
            line.tax_id = self.force_tax_id
        
        # ดำเนินการยืนยันคำสั่งซื้อ โดยข้ามการตรวจสอบเงื่อนไข
        return order.with_context(skip_mixed_check=True).action_confirm()
        
    def action_cancel(self):
        """
        ยกเลิกการปรับภาษี
        """
        return {'type': 'ir.actions.act_window_close'}