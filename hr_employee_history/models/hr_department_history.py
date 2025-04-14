# models/hr_department_history.py
from odoo import models, fields, api

class HrDepartmentHistory(models.Model):
    _name = 'hr.department.history'
    _description = 'Employee Department History'
    _order = 'date_end desc, date_start desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date')
    changed_by = fields.Many2one('res.users', string='Changed By', default=lambda self: self.env.user, readonly=True)