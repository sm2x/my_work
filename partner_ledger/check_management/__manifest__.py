# -*- coding: utf-8 -*-
{
    'name': "Check Management",

    'summary': """ Check Management  """,

    'description': """
        This Module is used for check \n
        It includes creation of check receipt ,check cycle ,Holding ....... \n

    """,

    'author': "Ahmed Farid ( KAMAH )",
    'website': "01008339922",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '12.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_accountant'],#' 'account_accountant', 'sale'

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'views/account_journal_view.xml',
        'views/checks_fields_view.xml',
        'views/check_payment.xml',
        'views/check_menus.xml',
        'wizard/check_cycle_wizard_view.xml',
        'views/payment_report.xml',
        'views/report_check_cash_payment_receipt_templates.xml',
        'data/sms_temp.xml',

    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'GPL-3',
    'price': 249.0,
    'currency': 'EUR',
    'application': True,

}
