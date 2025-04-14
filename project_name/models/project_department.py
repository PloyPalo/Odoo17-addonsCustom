from odoo import models, fields

class ProjectDepartment(models.Model):
    _name = 'project.department'
    _description = 'Project Departments'
    
    name = fields.Char(required=True)
    code = fields.Char(required=True)