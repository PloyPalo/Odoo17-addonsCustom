from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def action_delete_stock(self):
        self.sudo().unlink()
