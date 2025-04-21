{
    'name': 'Reorder App Menu',
    'version': '17.1.0.0',
    'category': 'Tools',
    'summary': 'Reorder applications in the main menu',
    'author': 'Palo Dev',
    'icon': 'web/static/lts/icon.png',
    'description': """
        This module allows you to reorder the applications in Odoo's main menu.
    """,
    'depends': ['base'],
    'data': [
        'views/ir_ui_menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}