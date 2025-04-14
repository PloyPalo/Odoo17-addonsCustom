from odoo import fields, models


class ProjectProjectStage(models.Model):
    """
       This model extends the 'project.task.type' model to include additional
       functionality for managing project task stages based on project accessibility.

       Attributes:
           project_access_ids (Selection): A Many2many field that specifies
                                              the type of project access
                                              (e.g., 'Manufacture', 'Trading').
       """
    _inherit = 'project.project.stage'

    project_access_ids = fields.Many2many('project.access',
                                          string="Project Access")

    def get_stage_ids(self):
        """
           Retrieves the stage IDs for a given project based on the user's project
           access level. If the user has 'admin' access, all stages for the project
           are returned. Otherwise, only stages matching the user's access type are returned.

           Returns:
               list: A list of IDs of the project stages accessible to the user.
               """
        user_access_level = self.env.user.project_access_ids
        if user_access_level.filtered(lambda access: access.is_admin):
            stage_ids = self.env['project.project.stage'].search([]).ids
        else:
            stage_ids = self.env['project.project.stage'].search([
                '|',
                ('project_access_ids', '=', False),
                ('project_access_ids', 'in', user_access_level.ids)
            ]).ids
        return stage_ids
