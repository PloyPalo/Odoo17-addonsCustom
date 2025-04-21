# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_invoice_level_setting = fields.Selection(
        [('summary', 'Summary'), ('line', 'Line by Line')],
        string="Tax Invoice Level",
        config_parameter='tax_invoice.default_tax_invoice_level',
        default='line',
        help="Determines how tax invoice data is stored:\n"
             "- Summary: One aggregated line per invoice.\n"
             "- Line by Line: One line per relevant invoice line.",
    )