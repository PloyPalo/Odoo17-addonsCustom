{
    'name': 'Sale Order Mix Tax',
    'version': '17.0.1.0.0',
    'author': 'Palo Dev',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_tax_view.xml',
        'views/sale_order_tax_confirmation_view.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
}

