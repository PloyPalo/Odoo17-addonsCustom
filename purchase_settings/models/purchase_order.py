from odoo import models, fields, api, _

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'
    
    partner_id = fields.Many2one('res.partner', required=False)
    show_partner_id = fields.Boolean(default=False)
    
    def button_confirm(self):
        if not self.partner_id:
            self.write({'show_partner_id': True})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'current',
                'flags': {'mode': 'edit'},
                'context': {'warning_message': 'Please select a vendor before confirming the order.'}
            }
        
        result = super().button_confirm()
        
        # แสดง rainbow_man หลังจาก confirm สำเร็จ
        return {
            'effect': {
                'fadeout': 'slow',
                'message': f'Purchase Order {self.name} created successfully',
                'type': 'rainbow_man'
            }
        }