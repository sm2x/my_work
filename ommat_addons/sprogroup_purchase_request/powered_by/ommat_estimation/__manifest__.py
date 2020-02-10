{
    'name': 'Ommat Project Estimation',
    'version': '12.0',
    'summary': 'GIT Project',
    'description': """  
    """,
    'author': "GIT",
    'category': 'Ommat Project Estimation',
    'website': 'http://www.git-eg.com',
    'depends': ['base', 'hr_appraisal', 'stock', 'mrp', 'account_accountant','purchase'],
    'data': [

        'security/ommat_group.xml',
        'security/ir.model.access.csv',
        'views/weight.xml',
        'views/estimation.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'sequence': 1,
    'application': True,

}
