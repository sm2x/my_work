# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 12 Accounting PDF Reports',
    'version': '12.0.1.0.0',
    'category': 'Invoicing Management',
    'summary': 'Accounting Reports For Odoo 12',
    'sequence': '10',
    'author': 'Odoo Mates, Odoo SA',
    'company': 'Odoo Mates',
    'maintainer': 'Odoo Mates',
    'support': 'odoomates@gmail.com',
    'website': '',
    'depends': ['account','check_management','account_accountant'],
    'live_test_url': 'https://www.youtube.com/watch?v=Qu6R3yNKR60',
    'demo': [],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/account_pdf_reports.xml',
        'wizards/partner_ledger.xml',
        'wizards/general_ledger.xml',
        'reports/report.xml',
        'reports/report_partner_ledger.xml',
        'reports/report_general_ledger.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'qweb': [],
}
