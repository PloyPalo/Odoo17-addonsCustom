from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# model อำเภอ
class District(models.Model):
    _name = 'res.district'
    _description = 'District'
    
    name = fields.Char(string='District Name', required=True)
    code = fields.Char(string='District Code', required=False)
    state_id = fields.Many2one('res.country.state', string='Province', required=True)

# model ตำบล
class SubDistrict(models.Model):
    _name = 'res.subdistrict'
    _description = 'Sub District'
    
    name = fields.Char(string='Sub District Name', required=True)
    code = fields.Char(string='Sub District Code', required=False)
    district_id = fields.Many2one('res.district', string='District', required=True)
    zip_code = fields.Char(string='Zip Code')
    
class ResPartner(models.Model):
    _inherit = "res.partner"

    branch = fields.Char(
        string="Tax Branch",
        copy=False,
        help="Branch ID, e.g., 0000, 0001, ...",
    )
    name_company = fields.Char(
        string="Company Name",
        index=True,
        translate=True,
    )
    
    firstname = fields.Char(translate=True)
    lastname = fields.Char(translate=True)
    name = fields.Char(translate=True)
    display_name = fields.Char(translate=True)

    # Address fields in res.partner model
    house_no = fields.Char(string="House No", required=False) #เลขที่
    moo = fields.Char(string='Moo', required=False) #หมู่ที่
    villa = fields.Char(string="Villa", required=False) #หมู่บ้าน
    alley = fields.Char(string="Alley", required=False) #ซอย
    sub_alley = fields.Char(string="Sub Alley", required=False) #แยก
    
    building = fields.Char(string="Building", required=False) #อาคาร
    floor = fields.Char(string="Floor", required=False) #ชั้น
    room_no = fields.Char(string="Room No", required=False) #ห้อง
    district_id = fields.Many2one('res.district', string='District')  # City อำเภอ/เขต
    subdistrict_id = fields.Many2one('res.subdistrict', string='Sub District') # ตำบล/แขวง
    country_id = fields.Many2one('res.country', string='Country', default=217) # Default Thailand
    zip = fields.Char(string='ZIP', related='subdistrict_id.zip_code', store=True, readonly=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_company') and vals.get('name_company'):
                vals['name'] = vals['name_company']
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('is_company') and vals.get('name_company'):
            vals['name'] = vals['name_company']
        return super().write(vals)

    @api.onchange('is_company')
    def _onchange_company_type(self):
        if self.is_company:
            self.name = self.name_company
        else:
            self.name = self._get_computed_name(self.lastname, self.firstname)

    @api.onchange('name_company')
    def _onchange_name_company(self):
        if self.is_company:
            self.name = self.name_company

    @api.constrains('vat', 'branch', 'company_id')
    def _check_vat_branch_unique(self):
        for record in self:
            if record.vat and record.branch:
                domain = [
                    ('vat', '=', record.vat),
                    ('branch', '=', record.branch),
                    ('company_id', '=', record.company_id.id),
                    ('id', '!=', record.id),
                ]
                if self.search_count(domain) > 0:
                    raise ValidationError(
                        _("Tax ID + Branch must be unique!")
                    )
                
    @api.onchange('subdistrict_id')
    def _onchange_subdistrict_id(self):
        """Update zip code when subdistrict changes"""
        if self.subdistrict_id:
            self.zip = self.subdistrict_id.zip_code
        else:
            self.zip = False

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            self.state_id = False
            self.district_id = False
            self.subdistrict_id = False
            self.zip = False 
            
    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            self.district_id = False
            self.subdistrict_id = False
            self.zip = False 
            
    @api.onchange('district_id')
    def _onchange_district_id(self):
        if self.district_id:
            self.subdistrict_id = False
            self.zip = False 