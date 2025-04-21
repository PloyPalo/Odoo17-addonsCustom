from odoo import fields, models

class HrEmployeeBase(models.AbstractModel): 
    #สร้างคลาสที่ใช้ เป็นพื้นฐานให้กับ class อื่น
    #ไม่มีตารางใน database, reuse code และเพิ่มความสามารถผ่าน inheritance
    
    _inherit = "hr.employee.base"

    name = fields.Char(translate=True)
