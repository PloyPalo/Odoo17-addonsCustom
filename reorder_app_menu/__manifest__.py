#Test
{
    "name": "Reorder App Menu",
    "version": "1.0.0",
    "category": "Tools",
    "summary": "เรียงลำดับรายการแอปในเมนูหลัก",
    "icon": "web/static/lts/icon.png",
    "author": "Light up Total Solution Public Company Limited",
    "website": "https://www.lightuptotal.co.th/",
    "description": """
        โมดูลนี้ช่วยให้คุณสามารถเรียงลำดับรายการแอปในเมนูหลักของ Odoo ได้
    """,
    "depends": ["base"],
    "data": [
        "views/ir_ui_menu_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}