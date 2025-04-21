from odoo import models, _
from odoo.exceptions import UserError

class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'
    
    def action_force_delete(self):
        for unbuild in self:
            if unbuild.state == 'done':
                # ใช้ SQL โดยตรงเพื่อลบข้อมูลที่เกี่ยวข้อง
                self.env.cr.execute("DELETE FROM stock_move_line WHERE move_id IN (SELECT id FROM stock_move WHERE unbuild_id = %s)", (unbuild.id,))
                self.env.cr.execute("DELETE FROM stock_move WHERE unbuild_id = %s", (unbuild.id,))
                self.env.cr.execute("DELETE FROM mrp_unbuild WHERE id = %s", (unbuild.id,))
                
                # อัปเดต cache
                self.env['stock.move']._invalidate_cache()
                self.env['mrp.unbuild']._invalidate_cache()
                
                # แทนที่จะใช้ reload tag ให้ redirect ไปยัง tree view
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Unbuild Orders',
                    'res_model': 'mrp.unbuild',
                    'view_mode': 'tree,form',
                    'target': 'main',
                    'context': {'create': False}, 
                }
        return True