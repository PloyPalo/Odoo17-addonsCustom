from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def check_mixed_product_types(self):
        """
        ตรวจสอบว่ามีทั้งสินค้าประเภท goods และ service ในรายการสั่งซื้อหรือไม่
        """
        self.ensure_one()
        if not self.order_line:
            return False, [], []
            
        goods_lines = []
        service_lines = []
        
        for line in self.order_line:
            if line.is_service:
                service_lines.append(line)
            else:
                goods_lines.append(line)
                
        # ตรวจสอบว่ามีทั้งสองประเภทหรือไม่
        has_mixed = bool(goods_lines) and bool(service_lines)
                
        return has_mixed, goods_lines, service_lines
    
    def check_mixed_tax_scopes(self):
        """
        ตรวจสอบว่ามีภาษีที่มี tax_scope เป็นทั้ง goods และ service ในรายการสั่งซื้อหรือไม่
        """
        self.ensure_one()
        if not self.order_line:
            return False, False, [], []
            
        goods_tax_lines = []
        service_tax_lines = []
        null_tax_scope_lines = []
        
        for line in self.order_line:
            for tax in line.tax_id:
                if tax.tax_scope == 'service':
                    if line not in service_tax_lines:
                        service_tax_lines.append(line)
                elif tax.tax_scope == 'consu':
                    if line not in goods_tax_lines:
                        goods_tax_lines.append(line)
                elif tax.tax_scope is None or tax.tax_scope == False:
                    if line not in null_tax_scope_lines:
                        null_tax_scope_lines.append(line)
        
        # ตรวจสอบว่ามีการผสมของ tax scope หรือไม่
        has_mixed_tax_scopes = bool(goods_tax_lines) and bool(service_tax_lines)
        has_null_tax_scope = bool(null_tax_scope_lines)
                    
        return has_mixed_tax_scopes, has_null_tax_scope, goods_tax_lines, service_tax_lines
    
    def check_missing_force_tax_invoice(self):
        """
        ตรวจสอบว่ามีภาษีที่ไม่ได้ถูกกำหนดให้เป็น force_tax_invoice หรือไม่
        """
        self.ensure_one()
        if not self.order_line:
            return False, []
            
        non_force_tax_lines = []
        has_any_force_tax = False
        
        # ค้นหาภาษีที่มีการกำหนดเป็น force_tax_invoice
        force_tax = self.env['account.tax'].search([('force_tax_invoice', '=', True)], limit=1)
        if not force_tax:
            # ถ้าไม่มีภาษีที่กำหนดเป็น force_tax_invoice ในระบบเลย
            for line in self.order_line:
                if line.tax_id:  # มีการกำหนดภาษี แต่ไม่มี force tax ในระบบ
                    non_force_tax_lines.append(line)
            return bool(non_force_tax_lines), non_force_tax_lines, None
        
        # ตรวจสอบภาษี (ไม่ปรับเปลี่ยนโดยอัตโนมัติ)
        for line in self.order_line:
            line_has_force_tax = False
            for tax in line.tax_id:
                if tax.force_tax_invoice:
                    line_has_force_tax = True
                    has_any_force_tax = True
                    break
            
            if not line_has_force_tax and line.tax_id:
                # เก็บบันทึกรายการที่ไม่มี force tax
                non_force_tax_lines.append(line)
        
        # ตรวจสอบว่ามีรายการที่ไม่มี force tax หรือไม่
        missing_force_tax = bool(non_force_tax_lines)
        
        return missing_force_tax, non_force_tax_lines, force_tax
    
    def has_multiple_order_lines(self):
        """
        ตรวจสอบว่ามีรายการสั่งซื้อมากกว่า 1 รายการหรือไม่
        """
        self.ensure_one()
        return len(self.order_line) > 1
    
    def check_all_conditions(self):
        """
        ตรวจสอบเงื่อนไขทั้งหมด
        """
        mixed_products, goods_lines, service_lines = self.check_mixed_product_types()
        mixed_tax_scopes, has_null_tax_scope, goods_tax_lines, service_tax_lines = self.check_mixed_tax_scopes()
        missing_force_tax, non_force_tax_lines, force_tax = self.check_missing_force_tax_invoice()
        has_multiple_lines = self.has_multiple_order_lines()
        
        return {
            'mixed_products': mixed_products,
            'goods_lines': goods_lines,
            'service_lines': service_lines,
            'mixed_tax_scopes': mixed_tax_scopes,
            'has_null_tax_scope': has_null_tax_scope,
            'goods_tax_lines': goods_tax_lines,
            'service_tax_lines': service_tax_lines,
            'missing_force_tax': missing_force_tax,
            'non_force_tax_lines': non_force_tax_lines,
            'force_tax': force_tax,
            'has_multiple_lines': has_multiple_lines
        }
    
    def action_confirm(self):
        """
        Override action_confirm เพื่อตรวจสอบเงื่อนไขผสมก่อนยืนยันคำสั่งซื้อ
        """
        # ตรวจสอบว่ามีการเรียกจาก wizard หรือไม่
        if self.env.context.get('skip_mixed_check'):
            return super(SaleOrder, self).action_confirm()
            
        for order in self:
            # ตรวจสอบเงื่อนไขทั้งหมด
            conditions = order.check_all_conditions()
            
            # ตรวจสอบว่ามีรายการสั่งซื้อมากกว่า 1 รายการหรือไม่
            if not conditions['has_multiple_lines']:
                # มีรายการเดียว ไม่จำเป็นต้องตรวจสอบเงื่อนไขผสม
                return super(SaleOrder, self).action_confirm()
                
            # 1. ตรวจสอบ tax_scope เป็น null (แจ้งเตือนก่อนเงื่อนไขอื่นๆ)
            if conditions['has_null_tax_scope']:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('ข้อควรระวัง'),
                        'message': _('พบรายการภาษีที่ไม่ได้ระบุ Tax Scope กรุณาตรวจสอบการตั้งค่าภาษีให้ถูกต้องก่อนดำเนินการต่อ'),
                        'type': 'warning',
                        'sticky': True,
                    }
                }
            
            # 2. ตรวจสอบภาษีที่ไม่มีการกำหนด force_tax_invoice
            if conditions['missing_force_tax']:
                # ตรวจสอบว่ามีภาษีที่ถูกกำหนดให้เป็น force_tax_invoice ในระบบหรือไม่
                if not conditions['force_tax']:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('ข้อควรระวัง'),
                            'message': _('ไม่พบภาษีที่กำหนดเป็น Force Tax Invoice กรุณาตั้งค่าก่อนดำเนินการต่อ'),
                            'type': 'warning',
                            'sticky': True,
                        }
                    }
                else:
                    # มีภาษี force_tax_invoice ในระบบ แต่ไม่ได้ถูกใช้ในคำสั่งซื้อนี้
                    # แสดง wizard ให้ผู้ใช้ยืนยันการใช้ force tax
                    return {
                        'name': _('Confirm Tax Update'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'sale.order.tax.confirmation',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {
                            'default_order_id': order.id,
                            'default_has_missing_force_tax': conditions['missing_force_tax'],
                            'default_force_tax_id': conditions['force_tax'].id
                        },
                    }
            
            # 3. ตรวจสอบการผสมกันของสินค้าหรือ tax_scope
            if conditions['mixed_products'] or conditions['mixed_tax_scopes']:
                return {
                    'name': _('Confirm Tax Update'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.order.tax.confirmation',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_order_id': order.id,
                        'default_has_mixed_products': conditions['mixed_products'],
                        'default_has_mixed_tax_scopes': conditions['mixed_tax_scopes']
                    },
                }
        
        # ไม่พบปัญหาใดๆ ดำเนินการยืนยันคำสั่งซื้อตามปกติ
        return super(SaleOrder, self).action_confirm()