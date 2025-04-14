{
    "name": "Contacts Partner",
    "version": "17.0.1.0.0",
    "author": "Light up Total Solution Public Company Limited",
    "website": "https://www.lightuptotal.co.th/",
    "category": "Contacts",
    "license": "LGPL-3",
    "icon": "web/static/lts/icon.png",
    "depends": [
        "base",
        "contacts",
        "partner_company_type",
        "partner_firstname",
        "hr"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "views/res_company_view.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_company_type_view.xml",
        "views/res_users_view.xml",
        "views/res_district_view.xml",
        "views/res_subdistrict_view.xml",
        "views/res_partner_list_view.xml",
        "data/res.partner.company.type.csv",
        "data/res.partner.title.csv",
        "data/res.district.csv",
        "data/res.subdistrict.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "contact_settings/static/src/css/contact_configurator.css",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
