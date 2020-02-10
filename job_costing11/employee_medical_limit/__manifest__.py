{
    'name': 'Employee Medical Limit',
    'category': 'Human Resources',
    'summary': 'Manages the Health Requests of an Employee',
    'description': "",
    'version': '1.1',
    'author': 'TheOdooGuy',
    'website': 'https://www.theodooguy.com',
    'depends': ['hr', 'base', 'account'],
    'images': ['images/main.png', 'images/main_screenshot.png'],
    'data': [
        'views/medical_request_view.xml',
        'views/hr_employee_view.xml',
        'views/request_configuration.xml',
        'security/ir.model.access.csv',
        'security/medical_request_security.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
