from odoo import models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_reset_draft(self):
        self.state = 'draft'
        for move in self.move_ids_without_package:
            move.state = 'draft'
