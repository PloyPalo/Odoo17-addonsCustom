from odoo import models, api

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    
    @api.model
    def get_user_roots(self):
        roots = super(IrUiMenu, self).get_user_roots()
        # เรียงลำดับโดยแปลงชื่อเป็นตัวพิมพ์ใหญ่ก่อนเปรียบเทียบ
        return roots.sorted(key=lambda r: (r.name or '').upper())
    
    @api.model
    def load_menus(self, debug):
        menus = super(IrUiMenu, self).load_menus(debug)
        if menus and 'children' in menus:
            # เรียงลำดับเมนูย่อยโดยแปลงชื่อเป็นตัวพิมพ์ใหญ่ก่อนเปรียบเทียบ
            sorted_menu_items = sorted(
                menus['children'],
                key=lambda x: x.get('name', '').upper() if isinstance(x.get('name', ''), str) else ''
            )
            menus['children'] = sorted_menu_items
        return menus
    
    @api.model
    def sort_menus_alphabetically(self):
        """เรียงเมนูระดับบนสุดตามลำดับตัวอักษร"""
        # ดึงเฉพาะเมนูระดับบนสุด (ไม่มี parent) และเรียงตามชื่อโดยไม่สนใจตัวพิมพ์เล็ก/พิมพ์ใหญ่
        root_menus = self.search([('parent_id', '=', False)], order='name')
        # เรียงลำดับเมนูตามชื่อโดยแปลงเป็นตัวพิมพ์ใหญ่ก่อนเปรียบเทียบ
        root_menus_sorted = root_menus.sorted(key=lambda menu: (menu.name or '').upper())
        
        # อัปเดตลำดับ (sequence) ตามชื่อ
        sequence = 10
        for menu in root_menus_sorted:
            menu.sequence = sequence
            sequence += 10
            
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }