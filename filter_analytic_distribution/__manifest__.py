{
    'name': 'Filter Analytic Distribution',
    'version': '17.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Filter Analytic Distribution',
    'author': 'Palo Dev',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'sale', 'analytic'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'filter_analytic_distribution/static/src/js/analytic_distribution.js',
            'filter_analytic_distribution/static/src/scss/analytic_distribution.scss'
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
