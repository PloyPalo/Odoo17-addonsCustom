from odoo import models, fields, api

class ProjectDeleteWizard(models.TransientModel):
    _name = 'project.delete.wizard'
    _description = 'Project Delete Confirmation'
    
    project_id = fields.Many2one('project.project', string='Project', required=True)
    
    def action_confirm_delete(self):
        """Delete the project after confirmation"""
        if self.project_id:
            self.project_id.unlink()
        return {'type': 'ir.actions.act_window_close'}