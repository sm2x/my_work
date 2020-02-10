# -*- coding: utf-8 -*-
{
    'name': "Cheque Payment",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '1.0',
    'category': 'Accounting &amp; Finance',
    'sequence': 14,

    # any module necessary for this one to work correctly
    'depends': ['account','account_accountant','mail', 'web'],

    # always loaded
    'data': [
        'views/menus.xml',
        'views/bank_view.xml',
        'views/cheque_payment_group.xml',
        'views/return_reason_view.xml',
        'views/cheque_config_settings.xml',
        'views/cheque_master.xml',
        'views/create_issue_books_view.xml',
        'views/lost_cheque_wizard.xml',
        'views/cancel_cheque_wizard.xml',
        'views/issue_cheque_wizard.xml',
        'views/return_cheque_view.xml',
        'views/clear_cheque_wizard.xml',
        
        'views/views.xml',
        'views/templates.xml',

        'report/cheque_payment_template.xml',
        'report/cheque_receipt_template.xml',
        'report/cheque_report.xml',

        'security/ir.model.access.csv',
        'data/demo.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}