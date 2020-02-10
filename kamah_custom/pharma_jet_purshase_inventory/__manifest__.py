# -*- coding: utf-8 -*-
{
    'name': "pharma_jet_purshase_inventory",

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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','stock','uom','sale_management','point_of_sale','report_xlsx','pharma_jet','inventory_report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/pharma_security.xml',
        'security/ir.model.access.csv',
        # 'wizard/discount_view.xml',
        'views/views.xml',
        'views/pharma_inventory_view.xml',
        'views/assets.xml',
        'views/view_inheritance.xml',
        'reports/product_balance_view.xml',
        'reports/items_sales_report.xml',
        'reports/items_sales_view.xml',
        'reports/product_balance_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}