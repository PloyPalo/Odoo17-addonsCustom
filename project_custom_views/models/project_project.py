from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = "project.project"

    current_user_project_access_ids = fields.Many2many(
        "project.access",
        compute="_compute_current_user_project_access_ids",
        store=False,
    )

    # Override stage_id field
    stage_id = fields.Many2one(
        'project.project.stage',
        domain="[('id', 'in', allowed_stage_ids)]",
        default=lambda self: self._get_default_stage_id(),
    )

    allowed_stage_ids = fields.Many2many(
        'project.project.stage',
        compute='_compute_allowed_stage_ids',
        store=False,
    )

    @api.depends('stage_id')
    def _compute_current_user_project_access_ids(self):
        """Compute the user's accessible project records, not just IDs"""
        project_access_records = self.env.user.project_access_ids
        if project_access_records.filtered(lambda access: access.is_admin):
            self.current_user_project_access_ids = self.env["project.access"].search([])
        else:
            self.current_user_project_access_ids = project_access_records

    @api.depends('current_user_project_access_ids')
    def _compute_allowed_stage_ids(self):
        """Compute allowed stages based on user's project access"""
        for project in self:
            if project.current_user_project_access_ids.filtered(lambda access: access.is_admin):
                project.allowed_stage_ids = self.env['project.project.stage'].search([])
            else:
                project.allowed_stage_ids = self.env['project.project.stage'].search([
                    '|',
                    ('project_access_ids', '=', False),
                    ('project_access_ids', 'in', project.current_user_project_access_ids.ids)
                ])

    def _get_default_stage_id(self):
        """Get default stage based on user's access"""
        user_access = self.env.user.project_access_ids
        domain = []
        if not user_access.filtered(lambda access: access.is_admin):
            domain = [
                '|',
                ('project_access_ids', '=', False),
                ('project_access_ids', 'in', user_access.ids)
            ]
        
        stages = self.env['project.project.stage'].search(domain, order='sequence', limit=1)
        return stages and stages[0].id or False