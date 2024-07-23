# -*- coding: utf-8 -*-

# Klystron Global LLC
# Copyright (C) Klystron Global LLC
# All Rights Reserved
# https://www.klystronglobal.com/

{
    'name': "kg_payment_details",
    'summary': "To show the sale order invoice payment details",
    'description': """Long description of module's purpose""",
    'sequence': '-100',
    'author': 'Klystron Global',
    'maintainer': 'Dojy Larsan',
    'website': "www.klystronglobal.com",
    'application': True,
    'depends': ['base', 'sale','stock'],
    'version': '17.0.1.0.0',
    'data': [
        'views/sale_order_view.xml',
    ],
}

