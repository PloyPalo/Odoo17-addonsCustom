{
    "name": "Standard Cost",
    "version": "17.0.1.0.0",
    "author": "Palo Dev",
    "category": "Inventory/Inventory",
    "summary": "Adds standard cost calculation and history tracking to products",
    "description": """
        This module adds standard cost functionality to products with the following features:
        - Standard cost calculation (percentage or fixed)
        - History tracking of standard cost changes
        - User tracking for cost updates
    """,
    "license": "LGPL-3",
    "depends": ["product", "stock", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_general.xml",  
        "views/standard_cost_history.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
    "auto_install": False,
}