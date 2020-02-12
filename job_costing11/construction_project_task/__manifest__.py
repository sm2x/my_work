# -*- coding: utf-8 -*-
{
    'name': "ConstructionProjectTask",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'material_purchase_requisitions', 'job_order_link_cost_sheet', 'account','purchase_requisition','odoo_job_costing_management','job_order_subcontracting','account_invoicing'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'report/subcontractor_report.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
