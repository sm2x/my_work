{
    'name': 'Ommat Employee ID  ',
    'version': '1.0',
    'category': '',
    'sequence': 14,
    'author': 'GIT',
    'company': 'GIT',
    'license': 'LGPL-3',
    'website': 'http://www.git-eg.com',
    'summary': '',
    'depends': ['base','hr','hr_attendance','hr_payroll'],
    'data': [

           'security/contact.xml',
           'security/ir.model.access.csv',
           'views/employee_contract.xml',
           'views/views.xml',
           'views/employee_id.xml',
           'views/resignation.xml',

            ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
