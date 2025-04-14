# models/ir_ui_menu.py
from odoo import models, api

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def get_user_roots(self):
        roots = super(IrUiMenu, self).get_user_roots()
        return roots.sorted('sequence')

    @api.model
    def load_menus(self, debug):
        menus = super(IrUiMenu, self).load_menus(debug)
        if menus and 'children' in menus:
            sorted_menu_items = sorted(menus['children'], key=lambda x: x.get('sequence', 100))
            menus['children'] = sorted_menu_items
        return menus