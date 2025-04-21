from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# model อำเภอ
class District(models.Model):
    _name = 'res.district'
    _description = 'District'
    
    name = fields.Char(string='District Name', required=True, translate=True)
    code = fields.Char(string='District Code', required=False)
    state_id = fields.Many2one('res.country.state', string='Province', required=True)

# model ตำบล
class SubDistrict(models.Model):
    _name = 'res.subdistrict'
    _description = 'Sub District'
    
    name = fields.Char(string='Sub District Name', required=True, translate=True)
    code = fields.Char(string='Sub District Code', required=False)
    district_id = fields.Many2one('res.district', string='District', required=True)
    zip_code = fields.Char(string='Zip Code')

# model จังหวัด 
class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    name = fields.Char(translate=True)
    code = fields.Char()    
    
    def name_get(self):
        result = []
        for record in self:
            if record.country_id.code == "TH":
                result.append((record.id, record.name))
            else:
                result.append(super(CountryState, record).name_get()[0])
        return result

# model partner contacts
class ResPartner(models.Model):
    _inherit = "res.partner"

    name_company = fields.Char(
        string="Company Name",
        index=True,
        translate=True,
    )
    
    # Add new fields for Head Office / Branch selection
    office_type = fields.Selection([
        ('head_office', _('Head Office')), 
        ('branch', _('Branch'))
    ], string=_("Office Type"))
    
    @api.depends('is_head_office')
    def _compute_is_branch_office(self):
        for partner in self:
            partner.is_branch_office = not partner.is_head_office
            
    branch = fields.Char(
        string=_("Tax Branch"),
        copy=False,
        help="Branch ID, e.g., 0000, 0001, ...",
        # required=False,  
    )
    
    @api.onchange('office_type')
    def _onchange_office_type(self):
        if self.office_type == 'head_office':
            self.branch = "00000"
        else:
            self.branch = False
            
    firstname = fields.Char(translate=True)
    lastname = fields.Char(translate=True)
    name = fields.Char(translate=True)
    display_name = fields.Char(translate=True)

    # Address fields in res.partner model
    house_no = fields.Char(string="House No", required=False) #เลขที่
    building = fields.Char(string="Building", required=False) #อาคาร
    room_no = fields.Char(string="Room No", required=False) #ห้อง
    floor = fields.Char(string="Floor", required=False) #ชั้น
    villa = fields.Char(string="Villa", required=False) #หมู่บ้าน
    moo = fields.Char(string="Moo", required=False) #หมู่ที่
    alley = fields.Char(string="Alley", required=False) #ซอย
    sub_alley = fields.Char(string="Sub Alley", required=False) #แยก
    street_name = fields.Char(string="Street", required=False) #ถนน Field ใหม่
    
    subdistrict_id = fields.Many2one('res.subdistrict', string="Sub District") #ตำบล/แขวง
    district_id = fields.Many2one('res.district', string="District")  #City อำเภอ/เขต
    country_id = fields.Many2one('res.country', string="Country") # ประเทศ

    street = fields.Char(compute='_compute_address_fields', store=True, readonly=False) 
    street2 = fields.Char(compute='_compute_address_fields', store=True, readonly=False) 
    city = fields.Char(compute='_compute_address_fields', store=True, readonly=False) #จังหวัด
    zip = fields.Char(string="ZIP", related='subdistrict_id.zip_code', store=True, readonly=True)
    
    @api.depends('house_no', 'building', 'room_no', 'floor', 'villa', 'moo', 'alley', 'sub_alley', 'street_name', 'district_id', 'subdistrict_id', 'state_id', 'country_id', 'zip')
    def _compute_address_fields(self):
        for partner in self:
            # กลุ่มที่ 1: เลขที่, อาคาร, ชั้น, ห้อง
            addr_parts1 = []
            if partner.house_no:
                addr_parts1.append(_("House No") + " " + partner.house_no)
            if partner.building:
                addr_parts1.append(_("Building %s") % partner.building)
            if partner.floor:
                addr_parts1.append(_("Floor %s") % partner.floor)
            if partner.room_no:
                addr_parts1.append(_("Room %s") % partner.room_no)
                
            # กลุ่มที่ 2: หมู่บ้าน, หมู่ที่, ซอย, แยก, ถนน
            addr_parts2 = []
            if partner.villa:
                addr_parts2.append(_("Villa %s") % partner.villa)
            if partner.moo:
                addr_parts2.append(_("Moo %s") % partner.moo)
            if partner.alley:
                addr_parts2.append(_("Alley %s") % partner.alley)
            if partner.sub_alley:
                addr_parts2.append(_("Sub Alley %s") % partner.sub_alley)
            if partner.street_name:
                addr_parts2.append(_("Street %s") % partner.street_name)
            
            # กำหนดค่าให้ฟิลด์มาตรฐานของ Odoo
            partner.street = " ".join(addr_parts1) if addr_parts1 else False
            partner.street2 = " ".join(addr_parts2) if addr_parts2 else False
            
            # ตำบล/แขวง,อำเภอ/เขต ใส่ในฟิลด์ city
            subdistrict_name = partner.subdistrict_id.name if partner.subdistrict_id else ""
            district_name = partner.district_id.name if partner.district_id else ""
            
            city_parts = []
            if subdistrict_name:
                city_parts.append(_("Sub-district %s") % subdistrict_name)
            if district_name:
                city_parts.append(_("District %s") % district_name)
            
            partner.city = " ".join(city_parts) if city_parts else False
            
    # ฟังก์ชันใหม่สำหรับการสร้างชื่อที่แสดงพร้อมประเภทสำนักงาน
    def _get_name_with_office_type(self):
        self.ensure_one()
        if not self.is_company:
            # ถ้าไม่ใช่บริษัท ไม่ต้องเพิ่มประเภทสำนักงาน
            return self.name
        
        # ใช้ชื่อบริษัทเป็นพื้นฐาน
        name = self.name_company or self.name
        
        # ถ้าไม่มีชื่อ ให้คืนค่าเดิม
        if not name:
            return self.name
        
        if self.office_type == 'head_office':
            return _("%s (Head Office)") % name
        elif self.office_type == 'branch' and self.branch:
            return _("%s (Branch No. %s)") % (name, self.branch)
        
        return name
    
    # อัปเดตชื่อเมื่อเปลี่ยนประเภทสำนักงาน
    def _update_display_name_with_office_type(self):
        if self.is_company:
            self.name = self._get_name_with_office_type()
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_company') and vals.get('name_company'):
                # ใช้ชื่อบริษัท
                base_name = vals['name_company']
                
                # ตรวจสอบว่ามีข้อมูลสำนักงานหรือไม่
                office_type = vals.get('office_type', 'head_office')
                branch = vals.get('branch', '00000')
                
                if office_type == 'head_office':
                    vals['name'] = _("%s (Head Office)") % base_name
                elif office_type == 'branch' and branch:
                    vals['name'] = _("%s (Branch No. %s)") % (base_name, branch)
                else:
                    vals['name'] = base_name
                
            elif not vals.get('is_company') and vals.get('firstname') and vals.get('lastname'):
                # สำหรับบุคคล ใช้ชื่อ-นามสกุลตามปกติ
                vals['name'] = self._get_computed_name(vals.get('firstname'), vals.get('lastname'))
        
        return super().create(vals_list)

    def write(self, vals):
        # ถ้ามีการอัปเดตชื่อบริษัทหรือประเภทสำนักงาน
        update_name = False
        
        if 'is_company' in vals:
            update_name = True
        
        if 'name_company' in vals and self.is_company:
            base_name = vals['name_company']
            office_type = vals.get('office_type', self.office_type)
            branch = vals.get('branch', self.branch)
            
            if office_type == 'head_office':
                vals['name'] = _("%s (Head Office)") % base_name
            elif office_type == 'branch' and branch:
                vals['name'] = _("%s (Branch No. %s)") % (base_name, branch)
            else:
                vals['name'] = base_name
            
        # เมื่อมีการเปลี่ยนประเภทสำนักงานหรือสาขา
        if ('office_type' in vals or 'branch' in vals) and self.is_company:
            office_type = vals.get('office_type', self.office_type)
            branch = vals.get('branch', self.branch)
            base_name = vals.get('name_company', self.name_company or self.name.split(' (')[0])
            
            if office_type == 'head_office':
                vals['name'] = _("%s (Head Office)") % base_name
            elif office_type == 'branch' and branch:
                vals['name'] = _("%s (Branch No. %s)") % (base_name, branch)
            else:
                vals['name'] = base_name
        
        return super().write(vals)

    @api.onchange('is_company')
    def _onchange_company_type(self):
        if self.is_company:
            if self.name_company:
                # อัปเดตชื่อที่แสดงรวมประเภทสำนักงาน
                self.name = self._get_name_with_office_type()
            else:
                self.name_company = self.name
                self.name = self._get_name_with_office_type()
        else:
            self.name = self._get_computed_name(self.lastname, self.firstname)
            self.office_type = False
            self.branch = False

    @api.onchange('name_company')
    def _onchange_name_company(self):
        if self.is_company:
            self.name = self._get_name_with_office_type()

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
    
    