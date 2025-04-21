{
    'name': 'Project Custom View',
    'version': '17.0.1.0.0',
    'category': 'Project',
    'summary': 'Project Custom View',
    'author': 'Palo Dev',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'project'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/project_access_data.xml',
        'data/project_task_access_data.xml',
        'views/project_task_type_view.xml',
        'views/project_project_stage_views.xml',
        'views/res_users_views.xml',
        'views/project_access_views.xml',
        'views/project_task_access_views.xml',
        'views/project_project_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_custom_views/static/src/js/ProjectKanbanRender.js',
            'project_custom_views/static/src/js/ProjectTaskKanbanRender.js'
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
