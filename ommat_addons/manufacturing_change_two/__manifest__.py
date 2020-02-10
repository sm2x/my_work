# -*- coding: utf-8 -*-
{
    'name': "Manufacturing Change Two",

    'summary': """
        Add New fields Manufacturing order Ban Bill of materials  """,

    'description': """
        --New Fields in bom
        -- New fields transferred from Bom to Manufacturing Order
        """,

    'author': "Ayman Samir",
    'website': "http://www.yourcompany.com",


    'category': 'mrp',
    'version': '0.1',

    'depends': ['base','mrp','ommat_catalogue',],


    'data': [

        'views/views.xml',

    ],


}
