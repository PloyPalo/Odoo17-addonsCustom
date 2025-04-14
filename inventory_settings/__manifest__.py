{
    "name": "Inventory Setting",
    "version": "17.0.1.0.0",
    "author": "Light up Total Solution Public Company Limited",
    "website": "https://www.lightuptotal.co.th/",
    "category": "Inventory",
    "license": "LGPL-3",
    "icon": "web/static/lts/icon.png",
    "depends": [
        "base",
        "sale",
        "sale_settings",
        "stock"
    ],
    "data": [
        "views/stock_move_line.xml",
        "views/detail_operation_view.xml",
        "views/stock_valuation_view.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
    "auto_install": False,
}
