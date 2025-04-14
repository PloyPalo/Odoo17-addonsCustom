from odoo import fields, models


class ResUsers(models.Model):
    """
    This model extends the 'res.users' model to include a selection field that
    specifies the project task access level for each user. The access level determines
    which project task stages the user can access.

    Attributes:
        project_access_ids (Many2many): Relationship to project access control.
        project_task_access_ids (Many2many): Relationship to project task access control.
    """
    _inherit = 'res.users'

    project_access_ids = fields.Many2many('project.access',
                                          string='Project Group')
    project_task_access_ids = fields.Many2many('project.task.access',
                                               string='Project Task Group')