from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)
class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    force_tax_invoice = fields.Boolean(
        string='Force Tax Invoice',
        default=False,
        help="เมื่อเลือกตัวเลือกนี้ ภาษีนี้จะถูกใช้สำหรับใบกำกับภาษีโดยไม่คำนึงถึงการตั้งค่าภาษีอื่นๆ"
    )
    
    @api.constrains('force_tax_invoice')
    def _check_only_one_force_tax_invoice(self):
        
        if self.force_tax_invoice:
            # ค้นหา Tax อื่นๆ ที่ถูกเลือกเป็น Force Tax Invoice
            other_taxes = self.search([('id', '!=', self.id), ('force_tax_invoice', '=', True), ('tax_scope', '=', self.tax_scope), ('type_tax_use', '=', self.type_tax_use)])
            # เปลี่ยนค่า force_tax_invoice เป็น False สำหรับ Tax อื่นๆ
            other_taxes.write({'force_tax_invoice': False})

    @api.onchange('force_tax_invoice')
    def _onchange_force_tax_invoice_check_tax_scope(self):
        
        if self.force_tax_invoice and (not self.tax_scope or self.tax_scope == 'none'):
            # ตั้งค่ากลับเป็น False เพื่อป้องกันการบันทึกผิดพลาด
            self.force_tax_invoice = False
            
            return {
                'warning': {
                    'title': _('Warning: Invalid Tax Scope'),
                    'message': _('You cannot force a tax invoice when the Tax Scope is not set or is set to "None". Please select a valid Tax Scope first.'),
                }
            }