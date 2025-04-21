from odoo import fields, models, _

class ProjectAccess(models.Model):
    """
    Model to manage access control for projects.

    Attributes:
        name (Char): The name of the access control entry.
        is_admin (Boolean): Indicates whether the access entry grants administrative privileges.
    """
    _name = 'project.access'
    _description = 'Project Access Control'
    
    name = fields.Char('Access Name', required=True, help="Name of the access control entry.")
    is_admin = fields.Boolean('Is Admin', help="Check if the user has administrative access.")