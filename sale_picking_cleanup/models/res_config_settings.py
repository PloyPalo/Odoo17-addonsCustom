from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    delete_draft_pickings = fields.Boolean(
        string="Auto-Delete Draft Pickings",
        config_parameter='sale_picking_cleanup.delete_draft_pickings',
        help="When enabled, draft/waiting/confirmed pickings will be deleted automatically when cancelling a sale order"
    )