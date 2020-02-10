from odoo import models, fields


class res_company(models.Model):
    _inherit = 'res.company'

    bank_acc = fields.Many2one('account.account', string='Bank Acc')
    medical_bill_account = fields.Many2one('account.account', string='Medical Account')
