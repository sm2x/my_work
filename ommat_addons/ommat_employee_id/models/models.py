from random import choice
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError


class EmployeeIdLoan(models.Model):
    _name = 'ommat.loan'

    loan_type = fields.Char(string='نوع القرض')
    loan_start_date = fields.Date(string='تاريخ بداية القرض')
    loan_end_date = fields.Date(string='تاريخ نهاية القرض')
    loan_total_amount= fields.Float(string='قيمة القرض')
    loan_installment = fields.Float(string='القسط الشهري')
    bank_name = fields.Many2one('ommat.bank',string='اسم البنك')

class EmployeeIdBank(models.Model):
    _name = 'ommat.bank'

    name = fields.Char(string='اسم البنك')
