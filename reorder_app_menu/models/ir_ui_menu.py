from odoo import models, api

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    
    @api.model
    def get_user_roots(self):
        roots = super(IrUiMenu, self).get_user_roots()
        return roots.sorted(key=lambda r: r.name or '')
    
    @api.model
    def load_menus(self, debug):
        menus = super(IrUiMenu, self).load_menus(debug)
        if menus and 'children' in menus:
            sorted_menu_items = sorted(
                menus['children'],
                key=lambda x: x.get('name', '') if isinstance(x.get('name', ''), str) else ''
            )
            menus['children'] = sorted_menu_items
        return menus
    
    @api.model
    def sort_menus_alphabetically(self):
        """เรียงเมนูระดับบนสุดตามลำดับตัวอักษร"""
        # ดึงเฉพาะเมนูระดับบนสุด (ไม่มี parent)
        root_menus = self.search([('parent_id', '=', False)], order='name')
        
        # อัปเดตลำดับ (sequence) ตามชื่อ
        sequence = 10
        for menu in root_menus:
            menu.sequence = sequence
            sequence += 10
            
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }