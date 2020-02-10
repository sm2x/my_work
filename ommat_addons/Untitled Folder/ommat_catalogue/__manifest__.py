# -*- coding: utf-8 -*-
{
    'name': "ommat_catalogue",

    'summary': """
        Poultry (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Poultry Solution 
    """,

    'author': "GIT Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Poultry',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','mrp_byproduct','sale_management',
                'stock_account', 'stock_enterprise', 'mrp','purchase',''
                                                                      ''],

    # always loaded
    'data': [
        'security/ommat_group.xml',
        'security/ir.model.access.csv',
        # 'views/othet_models.xml',
        'views/views.xml',
        # 'views/templates.xml',
        'views/bom_pro_category.xml',
        'views/account_journal_view.xml',
        'views/checks_fields_view.xml',
        'views/check_payment.xml',
        'views/check_menus.xml',
        'wizard/check_cycle_wizard_view.xml',
        'views/payment_report.xml',
        'views/report_check_cash_payment_receipt_templates.xml',
        'data/sms_temp.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',

    ],
    'application': True,
    'sequence': 2,
}