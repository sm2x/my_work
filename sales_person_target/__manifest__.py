# -*- coding: utf-8 -*-
{
    'name': "Sales Person Commission Target",

    'summary': """
       Sales Person Commission Target
    """,

    'description': """
         Module Features: \n
        1- Configure Sale Person Commission Target. \n
        2- Compute Sale Person Commission Target Achievement. \n
        3- Print Out For Sale Person Achieved Target. \n
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Sales',
    'version': '12.0.1',

    'depends': ['base', 'crm', 'sale', 'sale_management'],

    'data': [
        'security/ir.model.access.csv',
        'views/sales_target_view.xml',
        'views/target_achieved_view.xml',
        'views/target_view.xml',
        'reports/achieved_target_report.xml',
        'reports/salesperson_target_check.xml',
        'wizard/compute_sales_target.xml',
        'wizard/salesperson_target_check.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
