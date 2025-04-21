{
    'name': 'Product Image Import',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Import product images from a CSV file',
    'description': """
        Module to import multiple product images from a CSV file.
        - Supports import from CSV with ID and image path columns.
        - Displays an import summary report.
        - Allows specifying the image folder.
    """,
    'author': 'Palo Dev',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}