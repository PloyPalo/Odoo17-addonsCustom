from odoo import models, fields, api

class MailWizardInvite(models.TransientModel):
    _inherit = 'mail.wizard.invite'
    
    @api.model
    def default_get(self, fields):
        res = super(MailWizardInvite, self).default_get(fields)
        if 'partner_ids' in fields:
            res['partner_ids'] = [(6, 0, [182, 179])]
        return res