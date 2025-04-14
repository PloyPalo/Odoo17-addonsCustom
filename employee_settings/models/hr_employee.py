from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    employee_code = fields.Char(string="Employee Code")
    name_th = fields.Char(string="Employee Name (TH)")
    nick_name  = fields.Char(string="Nick Name")
    age = fields.Integer(string='Age', compute='_compute_age', store=False)
    start_date = fields.Date(string='Start Date')
    working_age = fields.Char(string='Working Age', compute='_compute_working_age', store=False)
    parent_id = fields.Many2one('hr.employee', string='Manager', compute="_compute_parent_id", store=True)
    
    @api.depends('department_id.manager_id')
    def _compute_parent_id(self):
        for record in self:
            record.parent_id = record.department_id.manager_id.id
            
    @api.depends('start_date')
    def _compute_working_age(self):
        for record in self:
            if record.start_date:
                delta = relativedelta(datetime.now(), record.start_date)
                record.working_age = f"{delta.years} ปี {delta.months} เดือน {delta.days} วัน"
            else:
                record.working_age = False
                
    @api.depends('birthday')
    def _compute_age(self):
       for record in self:
           if record.birthday:
               delta = relativedelta(datetime.now(), record.birthday)
               record.age = delta.years
           else:
               record.age = 0
               
    # Exist Fields in Work Address
        # private_street
        # private_street2
        # private_city
        # private_zip
        # private_country_id 
        # private_state_id
    
    private_district_id = fields.Many2one('res.district', string="District")
    private_subdistrict_id = fields.Many2one('res.subdistrict', string="Sub District")
    
    private_house_no = fields.Char(string="House No", required=False)
    private_moo = fields.Char(string="Moo", required=False)
    private_villa = fields.Char(string="Villa", required=False)
    private_alley = fields.Char(string="Alley", required=False)
    private_sub_alley = fields.Char(string="Sub", required=False)
    private_building = fields.Char(string="Building", required=False)
    private_floor = fields.Char(string="Floor", required=False)
    private_room_no = fields.Char(string="Room No", required=False)
    
    
    @api.onchange('private_subdistrict_id')
    def _onchange_subdistrict_id(self):
        """Update zip code when subdistrict changes"""
        if self.private_subdistrict_id:
            self.private_zip = self.private_subdistrict_id.zip_code
        else:
            self.private_zip = False

    @api.onchange('private_country_id')
    def _onchange_country_id(self):
        if self.private_country_id:
            self.private_state_id = False
            self.private_district_id = False
            self.private_subdistrict_id = False
            self.private_zip = False 
            
    @api.onchange('private_state_id')
    def _onchange_state_id(self):
        if self.private_state_id:
            self.private_district_id = False
            self.private_subdistrict_id = False
            self.private_zip = False 
            
    @api.onchange('private_district_id')
    def _onchange_district_id(self):
        if self.private_district_id:
            self.private_subdistrict_id = False
            self.private_zip = False 
