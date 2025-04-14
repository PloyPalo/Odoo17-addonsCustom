# models/hr_job_history.py
from odoo import models, fields, api

class HrJobHistory(models.Model):
    _name = 'hr.job.history'
    _description = 'Employee Job History'
    _order = 'date_end desc, date_start desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    job_id = fields.Many2one('hr.job', string='Job Position', required=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date')
    changed_by = fields.Many2one('res.users', string='Changed By', default=lambda self: self.env.user, readonly=True)