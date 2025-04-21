{
    'name': 'Employee Settings',
    'version': '17.0.1.0.0',
    'author': 'Palo Dev',
    'category': 'Employees',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'contacts',
        'contact_settings',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_employee_list_views.xml',
        'views/hr_employee_kanban_views.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
}
