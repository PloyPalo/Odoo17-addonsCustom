{
    'name': 'Tax Invoice Enhancement',
    'version': '17.0.1.0.0',
    'author': 'Palo Dev',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['sale', 'account', 'sale_management', 'sale_tax_invoice'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/res_config_settings_views.xml',
        'views/account_tax_invoice_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
