# models/hr_employee.py
from odoo import models, fields, api

class HrEmployee(models.Model):
   _inherit = 'hr.employee'

   def _create_history_from_messages(self):
       for employee in self:
           # สร้างประวัติของตำแหน่งปัจจุบัน
           if employee.job_id:
               current_job = self.env['hr.job.history'].search([
                   ('employee_id', '=', employee.id),
                   ('job_id', '=', employee.job_id.id),
                   ('date_end', '=', False)
               ], limit=1)
               
               if not current_job:
                   self.env['hr.job.history'].create({
                       'employee_id': employee.id,
                       'job_id': employee.job_id.id,
                       'date_start': employee.start_date or fields.Date.today(),  # ใช้ start_date ถ้ามี
                       'changed_by': self.env.user.id,
                   })

           # สร้างประวัติของแผนกปัจจุบัน
           if employee.department_id:
               current_dept = self.env['hr.department.history'].search([
                   ('employee_id', '=', employee.id),
                   ('department_id', '=', employee.department_id.id),
                   ('date_end', '=', False)
               ], limit=1)
               
               if not current_dept:
                   self.env['hr.department.history'].create({
                       'employee_id': employee.id,
                       'department_id': employee.department_id.id,
                       'date_start': employee.start_date or fields.Date.today(),  # ใช้ start_date ถ้ามี
                       'changed_by': self.env.user.id,
                   })

   @api.model
   def create(self, vals):
       # เรียกใช้ create เดิม
       record = super(HrEmployee, self).create(vals)
       
       # กำหนดวันที่เริ่มต้น
       start_date = vals.get('start_date') or fields.Date.today()
       
       # สร้างประวัติเมื่อสร้างพนักงานใหม่
       if vals.get('job_id'):
           self.env['hr.job.history'].create({
               'employee_id': record.id,
               'job_id': vals['job_id'],
               'date_start': start_date,  # ใช้ start_date จาก vals
               'changed_by': self.env.user.id,
           })
           
       if vals.get('department_id'):
           self.env['hr.department.history'].create({
               'employee_id': record.id,
               'department_id': vals['department_id'],
               'date_start': start_date,  # ใช้ start_date จาก vals
               'changed_by': self.env.user.id,
           })
           
       return record

   def write(self, vals):
       for employee in self:
           if vals.get('job_id') and vals['job_id'] != employee.job_id.id:
               # ปิดประวัติเก่า
               old_history = self.env['hr.job.history'].search([
                   ('employee_id', '=', employee.id),
                   ('date_end', '=', False)
               ], limit=1)
               if old_history:
                   old_history.write({'date_end': fields.Date.today()})
               
               # สร้างประวัติใหม่
               self.env['hr.job.history'].create({
                   'employee_id': employee.id,
                   'job_id': vals['job_id'],
                   'date_start': fields.Date.today(),  # ใช้วันที่ปัจจุบัน
                   'changed_by': self.env.user.id,
               })

           if vals.get('department_id') and vals['department_id'] != employee.department_id.id:
               # ปิดประวัติเก่า
               old_history = self.env['hr.department.history'].search([
                   ('employee_id', '=', employee.id),
                   ('date_end', '=', False)
               ], limit=1)
               if old_history:
                   old_history.write({'date_end': fields.Date.today()})
               
               # สร้างประวัติใหม่
               self.env['hr.department.history'].create({
                   'employee_id': employee.id,
                   'department_id': vals['department_id'],
                   'date_start': fields.Date.today(),  # ใช้วันที่ปัจจุบัน
                   'changed_by': self.env.user.id,
               })

       return super(HrEmployee, self).write(vals)

   def action_view_job_history(self):
       self.ensure_one()
       self._create_history_from_messages()
       return {
           'name': 'Job History',
           'type': 'ir.actions.act_window',
           'res_model': 'hr.job.history',
           'view_mode': 'tree,form',
           'domain': [('employee_id', '=', self.id)],
           'context': {'default_employee_id': self.id}
       }

   def action_view_department_history(self):
       self.ensure_one()
       self._create_history_from_messages()
       return {
           'name': 'Department History',
           'type': 'ir.actions.act_window',
           'res_model': 'hr.department.history',
           'view_mode': 'tree,form',
           'domain': [('employee_id', '=', self.id)],
           'context': {'default_employee_id': self.id}
       }