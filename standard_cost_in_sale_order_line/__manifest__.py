# -*- coding: utf-8 -*-
{
    'name': "standard_cost_in_sale_order_line",

    "version": "17.0.1.0.0",
    "author": "Light up Total Solution Public Company Limited",
    "website": "https://www.lightuptotal.co.th/",
    "category": "Product Customization",
    "license": "LGPL-3",
    "icon": "web/static/lts/icon.png",

    # any module necessary for this one to work correctly test
    'depends': [
        'sale_management',
        'product',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/standard_cost_in_sale_order.xml',
    ],
}

