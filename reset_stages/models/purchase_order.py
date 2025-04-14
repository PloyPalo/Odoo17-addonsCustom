from odoo import models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_reset_cancel(self):
        for order in self:
            order.state = 'cancel'
            for move in order.order_line.mapped('move_ids'):
                move.state == 'draft'

