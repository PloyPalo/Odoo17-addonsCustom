from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if vals.get('state', 'draft') == 'draft':
            # quotation sequence
            if not vals.get('name') or vals.get('name') == _('New'):
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.now())
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'sale.quotation', sequence_date=seq_date) or _('New')
        else:
            # sale order sequence
            if not vals.get('name') or vals.get('name') == _('New'):
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.now())
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'sale.order', sequence_date=seq_date) or _('New')
        
        return super(SaleOrder, self).create(vals)
    
    def action_confirm(self):
        for order in self:
            if order.name.startswith('QT'):
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.now())
                order.name = self.env['ir.sequence'].next_by_code(
                    'sale.order', sequence_date=seq_date) or order.name
        
        return super(SaleOrder, self).action_confirm()