# -*- coding: utf-8 -*-
{
    'name': "Standard Cost Configuration",

    "version": "17.0.1.0.0",
    "author": "Light up Total Solution Public Company Limited",
    "website": "https://www.lightuptotal.co.th/",
    "category": "Product Customization",
    "license": "LGPL-3",
    "icon": "web/static/lts/icon.png",

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_management',
    ],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
    ],
}

