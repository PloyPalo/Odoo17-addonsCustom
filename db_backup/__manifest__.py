{
    'name': 'Database Backup Manager',
    'version': '17.0.1.0.0',
    'summary': 'Manage database backups with scheduling',
    'description': """
        This module provides functionality to:
        - Backup databases manually
        - Schedule automatic backups
        - Configure backup location
        - Manage backup retention
        - Select File Download Pass (fields.Selection)
    """,
    'author': 'Palo Dev',
    'license': 'LGPL-3',
    'category': 'Administration',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/db_backup_view.xml',
        'views/db_restore_view.xml',
        'views/db_download_view.xml', 
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
