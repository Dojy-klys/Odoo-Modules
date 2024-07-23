# -*- coding: utf-8 -*-

# Klystron Global LLC
# Copyright (C) Klystron Global LLC
# All Rights Reserved
# https://www.klystronglobal.com/

{
    'name': 'Quick Search',
    'version': '17.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['base','sale','purchase','stock'],
    'sequence': '-100',
    'author': 'Klystron Global',
    'maintainer': 'Dojy Larsan',
    'website': "www.klystronglobal.com",
    'application': True,
    'description': """The Module provide Quick search on Sales Order and Purchase Order""",
    'data': [
        'security/ir.model.access.csv',
        'wizard/quick_search_wizard_view.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'kg_quick_search/static/src/js/quick_search.js',
             'kg_quick_search/static/src/xml/quick_search.xml',
        ],},
    'images': ['static/description/banner.png'],
    "installable": True,
    'demo': [],

}