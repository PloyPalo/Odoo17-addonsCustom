from odoo import models, fields, api
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
        years = range(current_year - 3, current_year + 3)
        return [(str(year), str(year)) for year in years]

    def _get_next_sequence_number(self):
        last_project = self.search([
            ('project_group_id', '=', self.project_group_id.id),
            ('department_id', '=', self.department_id.id),
            ('year', '=', self.year),
            ('sequence_number', '!=', False)
        ], order='sequence_number desc', limit=1)
        
        if last_project:
            return last_project.sequence_number + 1
        return 1

    @api.depends('department_id', 'project_group_id', 'customer_abbr', 'project_name', 'year')
    def _compute_name(self):
        for record in self:
            if not all([record.department_id, record.project_group_id, record.project_name, record.year]):
                record.name = record.project_name if record.project_name else 'New Project'
                continue
                
            year = str(record.year)[-2:]
            
            # ถ้ามี sequence_number อยู่แล้วให้ใช้ค่าเดิม
            if record.sequence_number:
                sequence = str(record.sequence_number).zfill(3)
            else:
                sequence = str(record._get_next_sequence_number()).zfill(3)
                
            if record.customer_abbr:
                record.name = f"{record.department_id.code}-{record.project_group_id.code}-{year}{sequence}-{record.customer_abbr}:{record.project_name}"
            else:
                record.name = f"{record.department_id.code}-{record.project_group_id.code}-{year}{sequence}:{record.project_name}"
            
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
                
                project._create_default_stages()
        
        return projects

    def write(self, vals):
        fields_trigger = ['department_id', 'project_group_id', 'customer_abbr', 'project_name', 'year']
        needs_recompute = any(field in vals for field in fields_trigger)
        
        result = super().write(vals)
        
        if needs_recompute:
            for record in self:
                if not record.analytic_account_id:
                    analytic_account = record._create_analytic_account()
                    record.analytic_account_id = analytic_account.id
                else:
                    record.analytic_account_id.name = record.name
                    
        return result

