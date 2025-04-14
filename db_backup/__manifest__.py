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
        - 1.1 > 1.2
    """,
    'author': 'Light up Total Solution Public Company Limited',
    'website': 'https://www.lightuptotal.co.th/',
    'license': 'LGPL-3',
    'category': 'Administration',
    #'icon': 'web/static/lts/icon.png',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/db_backup_view.xml',
        'views/db_restore_view.xml',
        'views/db_download_view.xml', 
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
