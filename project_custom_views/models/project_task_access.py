from odoo import fields, models

class ProjectTaskAccess(models.Model):
    """
    Model to manage access control for project tasks.

    Attributes:
        name (Char): The name of the access control entry.
        is_admin (Boolean): Indicates whether the access entry grants administrative privileges.
    """
    _name = 'project.task.access'

    name = fields.Char('Access Name', required=True, help="Name of the access control entry.")
    is_admin = fields.Boolean('Is Admin', help="Check if the user has administrative access.")
