from odoo import models, fields

class ProjectDepartment(models.Model):
    _name = 'project.department'
    _description = 'Project Departments'
    
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    stage_ids = fields.One2many('project.department.stage', 'department_id', string='Task Stages')
    task_template_ids = fields.One2many('project.department.task.template', 'department_id', string='Task Templates')
    member_ids = fields.Many2many('res.partner', 'project_department_partner_rel',
                                  'department_id', 'partner_id',
                                  string='Default Invitation Project')
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Department code must be unique!')
    ]
    
class ProjectDepartmentStage(models.Model):
    _name = 'project.department.stage'
    _description = 'Department Task Stage Template'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True)
    department_id = fields.Many2one('project.department', string='Department', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    fold = fields.Boolean(string='Folded in Kanban', default=False, 
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    active = fields.Boolean(default=True)


class ProjectDepartmentTaskTemplate(models.Model):
    _name = 'project.department.task.template'
    _description = 'Department Task Template'
    _order = 'sequence, id'

    name = fields.Char(string='Task Name', required=True)
    department_id = fields.Many2one('project.department', string='Department', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Html(string='Description')
    active = fields.Boolean(default=True)