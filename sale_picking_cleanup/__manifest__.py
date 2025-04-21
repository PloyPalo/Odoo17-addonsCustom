{
    'name': 'Enhanced Sale Order Cancellation',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'author': 'Palo Dev',
    'summary': 'Automatically delete draft, waiting, confirmed and cancelled receipts when cancelling sale orders',
    'description': """
        Enhanced Sale Order Cancellation
        ================================
        This module extends the standard cancellation process of sale orders.
        When a sale order is cancelled, all related stock pickings (receipts) in draft, waiting, or confirmed state are automatically deleted.

        Features:
        ---------
        * Automatically delete related receipts in draft, waiting, or confirmed state when cancelling a sale order
        * Display notification with the number of deleted receipts
        * Seamlessly integrates with the standard cancel button on sale orders
        """,
    'depends': [
        'sale',
        'sale_management',
        'stock',
    ],
    'data': [
        'views/sale_order_cleanup.xml',  
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}