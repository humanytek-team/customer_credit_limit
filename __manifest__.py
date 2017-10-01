# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner Credit Limit',
    'version': '10',
    'category': 'Partner',
    'depends': ['account', 'sale'],
    'license': 'AGPL-3',
    'author': 'Humanytek',
    'summary': 'Set credit limit warning',
    'description': '''Partner Credit Limit'
        Checks for all over due payment and already paid amount
        if the difference is positive and acceptable then Salesman
        able to confirm SO
    ''',
    'data': [
        'security/groups.xml',
        'views/partner_view.xml',
        'views/wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
