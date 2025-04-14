from odoo import fields, models

class ProjectTaskType(models.Model):
    """
       This model extends the 'project.task.type' model to include additional
       functionality for managing project task stages based on project accessibility.

       Attributes:
           project_task_access_ids (Selection): A Many2many field that specifies
                                              the type of project access
                                              (e.g., 'Manufacture', 'Trading').
       """
    _inherit = 'project.task.type'

    project_task_access_ids = fields.Many2many('project.task.access',
                                               string="Project Task Access")

    def get_stage_ids(self, project_id):
        """
           Retrieves the stage IDs for a given project based on the user's project
           access level. If the user has 'admin' access, all stages for the project
           are returned. Otherwise, only stages matching the user's access type are returned.

           Args:
               project_id (int): The ID of the project for which stages are to be fetched.

           Returns:
               list: A list of IDs of the project stages accessible to the user.
               """
        user_access_level = self.env.user.project_task_access_ids
        if user_access_level.is_admin:
            stage_ids = self.env['project.task.type'].search(
                [('project_ids', 'in', [project_id])]).ids
        else:
            stage_ids = self.env['project.task.type'].search([
                '|',
                ('project_task_access_ids', '=', False),
                ('project_task_access_ids', 'in', user_access_level.ids),
                ('project_ids', 'in', [project_id])
            ]).ids
        return stage_ids
