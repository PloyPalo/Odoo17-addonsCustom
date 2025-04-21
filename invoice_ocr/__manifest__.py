{
    'name': 'Invoice OCR',
    'version': '',
    'summary': 'OCR for invoices and receipts',
    'description': """
        This module adds OCR capabilities to Odoo 17 for reading invoices and receipts.
        Features:
        - Process documents using Tesseract OCR or external OCR services
        - Extract key information from invoices and receipts
        - Automatically create draft invoices from scanned documents
        - Support for Thai and English languages
    """,
    'category': 'Accounting',
    'author': 'Palo Dev',
    'license': 'LGPL-3',
    'depends': ['base', 'account', 'documents'],
    'data': [
        'security/ir.model.access.csv',
        'views/ocr_config_views.xml',
        'views/document_views.xml',
        'views/menu_items.xml',
    ],
    'external_dependencies': {
        'python': ['pytesseract', 'pdf2image', 'numpy', 'opencv-python'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}