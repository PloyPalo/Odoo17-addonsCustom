{
    'name': 'Employee History',
    'version': '17.0.1.0.0',
    'summary': 'Track employee job positions and department history',
    'description': """
        Module to track employee history:
        - Job Positions History
        - Department History
    """,
    'author': ' Light up Total Solution Public Company Limited',
    "website": "https://www.lightuptotal.co.th/",
    "license": "LGPL-3",
    'category': 'Human Resources',
    "icon": "web/static/lts/icon.png",
    'depends': ['hr'],
    'data': [
        'views/hr_job_history_views.xml',
        'views/hr_department_history_views.xml',
        'views/hr_employee_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}