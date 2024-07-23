# -*- coding: utf-8 -*-

# Klystron Global LLC
# Copyright (C) Klystron Global LLC
# All Rights Reserved
# https://www.klystronglobal.com/

{
    'name': 'Portal HR',
    'version': '17.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['portal'],
    'sequence': '-100',
    'category': 'portal',
    'author': 'Klystron Global',
    'maintainer': 'Dojy Larsan',
    'website': "www.klystronglobal.com",
    'application': True,
    'description': """The Module provide Employee creation from Portal""",
    'data': [
        'views/portal_menu.xml',
        # 'security/ir.model.access.csv',
        # 'wizard/quick_search_wizard_view.xml',
    ],

    "installable": True,
    'demo': [],

}