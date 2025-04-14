from odoo import api,models, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_reset_draft(self):
        for order in self:
            # cancel MO
            order.state = 'cancel'
            
            # ค้นหา Stock Picking ที่เกี่ยวข้อง
            pickings = self.env["stock.picking"].search([
                "|",
                ("origin", "=", order.name),
                ("group_id", "=", order.procurement_group_id.id)
            ])
            
            # เปลี่ยนสถานะ Stock Picking เป็น cancel
            for picking in pickings:
                if picking.state == 'done':
                    picking.action_cancel()  # เรียกใช้ฟังก์ชัน action_cancel
                    picking.state = 'cancel'
                elif picking.state != 'cancel':  # ถ้ายังไม่ถูกยกเลิก
                    picking.action_cancel()
            
            # ค้นหา Stock Moves ที่เกี่ยวข้องกับ MO
            stock_moves = self.env["stock.move"].search([
                "|",
                ("raw_material_production_id", "=", order.id),
                ("production_id", "=", order.id)
            ])
            
            # จัดการ Stock Moves และ Move Lines
            if stock_moves:
                # เปลี่ยนสถานะ Stock Moves เป็น cancel
                for move in stock_moves:
                    if move.state == 'done':
                        move.state = 'cancel'
                    elif move.state != 'cancel':  # ถ้ายังไม่ถูกยกเลิก
                        move._action_cancel()
                
                # ค้นหา Stock Move Lines
                move_lines = self.env["stock.move.line"].search([
                    ("move_id", "in", stock_moves.ids)
                ])
                
                # เปลี่ยนสถานะ Stock Move Lines เป็น cancel
                for line in move_lines:
                    if line.state == 'done':
                        line.state = 'cancel'

    def action_delete_mo(self):
        for order in self:
            # ค้นหา Stock Moves
            stock_moves = self.env["stock.move"].search([
                "|",
                ("raw_material_production_id", "=", order.id),
                ("production_id", "=", order.id)
            ])

            # ตรวจสอบว่ามี stock moves ที่ done แล้วหรือไม่
            if stock_moves.filtered(lambda m: m.state == 'done'):
                raise UserError(_("Deletion is not possible as there are completed stock movements.\nPlease create a return document instead."))
                
            # ยกเลิก MO
            order.action_cancel()
            order.state = 'cancel'

            # ค้นหาและลบ Work Orders (WO)
            work_orders = self.env["mrp.workorder"].search([("production_id", "=", order.id)])
            if work_orders:
                work_orders.action_cancel()
                work_orders.unlink()

            # ค้นหาและลบ Stock Picking
            pickings = self.env["stock.picking"].search([
                "|",
                ("origin", "=", order.name),
                ("group_id", "=", order.procurement_group_id.id)
            ])
            
            for picking in pickings:
                if picking.state == "done":
                    raise UserError(_("Completed Stock Picking cannot be deleted!"))
                picking.action_cancel()
                picking.unlink()

            # จัดการ Stock Moves ที่ยังไม่ done
            if stock_moves:
                move_lines = self.env["stock.move.line"].search([
                    ("move_id", "in", stock_moves.ids)
                ])
                
                if move_lines:
                    move_lines.unlink()
                
                stock_moves.filtered(lambda m: m.state != 'done')._action_cancel()
                stock_moves.filtered(lambda m: m.state != 'done').unlink()

            # ลบ MO
            order.unlink()
            
        # Return action to go back to Manufacturing Orders
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacturing Orders',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'target': 'main',
        }

