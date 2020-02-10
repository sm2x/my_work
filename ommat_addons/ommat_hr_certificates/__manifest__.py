{
    'name': 'Ommat HR Certificates  ',
    'version': '1.0',
    'category': '',
    'sequence': 14,
    'author': 'GIT',
    'company': 'GIT',
    'license': 'LGPL-3',
    'website': 'http://www.git-eg.com',
    'summary': '',
    'depends': ['base','hr','hr_holidays','ommat_employee_id'],
    'data': [

           # 'security/contact.xml',
           # 'security/ir.model.access.csv',
           'reports/to_whom_concern_certificate.xml',
           'reports/work_certificate.xml',
           'reports/clearance_certificate.xml',
           'reports/thanking_certificate.xml',
           'reports/experience_certificate.xml',
           'views/certificates.xml',


            ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
