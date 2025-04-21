from odoo import _, api, fields, models
from odoo.exceptions import UserError, AccessError
from datetime import datetime

class ProjectProject(models.Model):
    _inherit = 'project.project'

    department_id = fields.Many2one('project.department', string='Department', required=True)
    project_group_id = fields.Many2one('project.group', string='Project Group', required=True)
    customer_abbr = fields.Char(string='Customer Abbreviation', required=False)
    project_name = fields.Char(string='Project Name', required=True)
    year = fields.Selection(selection='_get_year_selection', string='Year', required=True, default=lambda self: str(datetime.now().year))
    name = fields.Char(compute='_compute_name', store=True, readonly=True, required=True, default='New Project')
    sequence_number = fields.Integer(string='Sequence Number', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', copy=False)
  
    _sql_constraints = [
        ('unique_project_sequence', 
         'unique(department_id,project_group_id,year,sequence_number)',
         'Project sequence must be unique for the same department, group and year!')
    ]

    _indexes = [
        ('department_id', 'project_group_id', 'year', 'sequence_number')
    ]
    
    @api.onchange('department_id')
    def _onchange_department_id(self):
        self.ensure_one()
        if self.department_id:
            self.project_group_id = False
            domain = [('department_id', '=', self.department_id.id)]
        else:
            domain = []

        return {'domain': {'project_group_id': domain}}

    def _get_year_selection(self):
        current_year = datetime.now().year
        years = range(current_year - 2, current_year + 3)
        return [(str(year), str(year)) for year in years]

    def _get_next_sequence_number(self):
        """
        Get the next sequence number for the project.
        If department, group, or year has changed, this will find the highest
        sequence number for the new combination and return the next number.
        """
        # Find the highest sequence number for the current department, group and year
        last_project = self.search([
            ('project_group_id', '=', self.project_group_id.id),
            ('department_id', '=', self.department_id.id),
            ('year', '=', self.year),
            ('sequence_number', '!=', False)
        ], order='sequence_number desc', limit=1)

        if last_project:
            # If we found a project with the same department, group and year,
            # use its sequence number + 1
            return last_project.sequence_number + 1
        else:
            # If no project exists with this combination, start from 1
            return 1

    @api.depends('department_id', 'project_group_id', 'customer_abbr', 'project_name', 'year')
    def _compute_name(self):
        for record in self:
            if not all([record.department_id, record.project_group_id, record.project_name, record.year]):
                record.name = record.project_name if record.project_name else 'New Project'
                continue

            year = str(record.year)[-2:]

            if record.sequence_number:
                sequence = str(record.sequence_number).zfill(3)
            else:
                sequence = str(record._get_next_sequence_number()).zfill(3)

            if record.customer_abbr:
                record.name = f"{record.department_id.code}-{record.project_group_id.code}-{year}{sequence}-{record.customer_abbr}:{record.project_name}"
            else:
                record.name = f"{record.department_id.code}-{record.project_group_id.code}-{year}{sequence}:{record.project_name}"

    def _create_department_stages(self):
        """Create department-specific task stages for the project"""
        if not self.department_id:
            return self._create_default_stages()

        # Get department stages
        department_stages = self.department_id.stage_ids

        if not department_stages:
            return self._create_default_stages()

        # Create stages based on department templates
        for stage_template in department_stages:
            self.env['project.task.type'].sudo().create({
                'name': stage_template.name,
                'sequence': stage_template.sequence,
                'project_ids': [(4, self.id)],
                'fold': stage_template.fold,
            })

    def _create_department_tasks(self):
        """Create department-specific tasks for the project"""
        if not self.department_id:
            return

        # Get department task templates
        department_tasks = self.department_id.task_template_ids

        if not department_tasks:
            return

        # Get default stage for new tasks
        default_stage = self.env['project.task.type'].search([
            ('project_ids', 'in', self.id)
        ], order='sequence', limit=1)

        # Create tasks based on department templates
        for task_template in department_tasks:
            self.env['project.task'].sudo().create({
                'name': task_template.name,
                'project_id': self.id,
                'description': task_template.description,
                'stage_id': default_stage.id if default_stage else False,
                'sequence': task_template.sequence,
                'company_id': self.company_id.id,
                'user_ids': False, # Clear assigned users
            })

    def _create_default_stages(self):
        """Create default task stages for the project"""
        stages_data = [
            {'name': 'Todo', 'sequence': 1},
            {'name': 'In Progress', 'sequence': 2},
            {'name': 'Done', 'sequence': 3},
            {'name': 'Cancelled', 'sequence': 4},
        ]

        for stage_values in stages_data:
            self.env['project.task.type'].sudo().create({
                'name': stage_values['name'],
                'sequence': stage_values['sequence'],
                'project_ids': [(4, self.id)],
                'fold': stage_values['name'] in ['Done', 'Cancelled'],
            })

    def _create_analytic_account(self):
        """Create analytic account for the project"""
        default_plan = self.env['account.analytic.plan'].search([], limit=1)

        analytic_account = self.env['account.analytic.account'].create({
            'name': self.name,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'company_id': self.company_id.id,
            'plan_id': default_plan.id if default_plan else False,
            'project_ids': [(4, self.id)],
        })

        analytic_account.write({
            'project_ids': [(4, self.id)],
            'project_count': 1,
        })

        return analytic_account

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        for project in projects:
            if project.department_id and project.project_group_id and project.year:
                project.sequence_number = project._get_next_sequence_number()

                analytic_account = project._create_analytic_account()
                project.write({
                    'analytic_account_id': analytic_account.id,
                })

                # Create department-specific stages and tasks
                project._create_department_stages()
                project._create_department_tasks()

        return projects

    def _reorder_affected_projects(self, changed_project, original_values):
        """
        Reorder sequence numbers for projects affected by changes in a project's
        department, group, or year.
        
        This ensures that sequence numbers remain continuous and unique when
        projects are moved between different department/group/year combinations.
        """
        # If the project was moved from one combination to another,
        # we need to reorder the projects in the original combination
        if original_values:
            # Get the original department, group, and year values
            orig_dept_id = original_values.get('department_id', changed_project.department_id).id
            orig_group_id = original_values.get('project_group_id', changed_project.project_group_id).id
            orig_year = original_values.get('year', changed_project.year)
            
            # Find all projects in the original combination
            original_projects = self.env['project.project'].search([
                ('department_id', '=', orig_dept_id),
                ('project_group_id', '=', orig_group_id),
                ('year', '=', orig_year),
                ('id', '!=', changed_project.id),
            ], order='sequence_number')
            
            # Reorder sequence numbers to close any gaps
            for i, project in enumerate(original_projects):
                seq_number = i + 1
                if project.sequence_number != seq_number:
                    project.write({'sequence_number': seq_number})
                    # Force name recomputation
                    project._compute_name()
        
        # Now ensure the projects in the new combination have sequential numbers
        current_projects = self.env['project.project'].search([
            ('department_id', '=', changed_project.department_id.id),
            ('project_group_id', '=', changed_project.project_group_id.id),
            ('year', '=', changed_project.year),
        ], order='sequence_number')
        
        # Check for gaps or duplicate sequence numbers
        expected_seq = 1
        needs_resequence = False
        
        for project in current_projects:
            if project.sequence_number != expected_seq:
                needs_resequence = True
                break
            expected_seq += 1
        
        # Resequence if needed
        if needs_resequence:
            for i, project in enumerate(current_projects):
                seq_number = i + 1
                if project.sequence_number != seq_number:
                    project.write({'sequence_number': seq_number})
                    # Force name recomputation
                    project._compute_name()
    
    # delete button for project
    def action_delete_project(self):
        """
        Delete the project and related records after confirmation
        """
        self.ensure_one()
        
        # Add confirmation dialog
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delete Project',
            'res_model': 'project.delete.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_project_id': self.id},
        }