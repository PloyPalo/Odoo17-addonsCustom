from odoo import models, fields

class ProjectGroup(models.Model):
    _name = 'project.group'
    _description = 'Project Groups'
    
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    department_id = fields.Many2one('project.department', string='Department', required=True)