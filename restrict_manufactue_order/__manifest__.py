{
    "name": "Restrict Manufacture Order",
    "version": "17.0.1.0.0",
    "category": "Manufacture",
    "summary": """Restrict Manufacture Order""",
    "author": "Light up Total Solution Public Company Limited",
    "website": "https://www.lightuptotal.co.th/",
    "license": "LGPL-3",
    "icon": "web/static/lts/icon.png",
    "depends": [
        "base", 
        "stock", 
        "mrp", 
        "purchase", 
        "base_setup"
    ],
    "data": [
        "views/res_config_settings_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
