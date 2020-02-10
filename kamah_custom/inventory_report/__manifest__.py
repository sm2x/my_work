# -*- coding: utf-8 -*-
{
    'name': "inventory_report",

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
    'category': 'Uncategorized',
    'version': '2',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','account_accountant'],

    # always loaded
    'data': [
        'security/inventory_report_security.xml',
        'security/ir.model.access.csv',
        'views/stock_card_view.xml',
        'views/product_card_view.xml',
        'views/transfer_report_view.xml',
        'views/total_inventory_view.xml',
        'views/scrap_product_view.xml',
        'views/sale_to_purchase_percentage_view.xml',
        'views/inventory_adjustment_view.xml',
        'views/bonus_view.xml',
        'views/items_sales_view.xml',
        'views/product_balance_stock_view.xml',
        'reports/stock_card_report.xml',
        # 'reports/p_ll_report.xml',
        'reports/product_card_report.xml',
        'reports/product_list_report.xml',
        'reports/transfer_report.xml',
        'reports/total_inventory_report.xml',
        'reports/scrap_product_report.xml',
        'reports/bonus_report.xml',
        'reports/inventory_adjustment_report.xml',
        'reports/items_sales_report.xml',
        'reports/product_balance_stock_report.xml',
        'reports/sale_to_percentage_report.xml',
        'reports/product_report.xml',
        'views/item_card_view.xml',
        'views/partner_ledger_view.xml',
        'views/products_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}