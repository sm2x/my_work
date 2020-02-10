from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MedicalRequest(models.Model):
    _name = 'medical.request'

    @api.depends('lines_id.amount')
    def _compute_amount(self):
        for rec in self:
            total_score = 0.0
            for record in rec.lines_id:
                total_score += record.amount
            rec.update({'total_amount': total_score})

    name = fields.Char(string='Medical Request', readonly=1)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  default=lambda self: self.env['hr.employee'].browse(self.env.user.id))
    employee_dept = fields.Many2one('hr.department', related='employee_id.department_id', string="Department",
                                    readonly=1)
    job_title = fields.Many2one('hr.job', related='employee_id.job_id', string='Job Title', readonly=1)
    lines_id = fields.One2many('medical.details.line', 'medical_id')
    medical_bills = fields.Binary(string='Medical Bills')
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_amount')
    employee_credit = fields.Float(string='Credit', related='employee_id.medical_limit', readonly=1, required=True)
    state = fields.Selection([('draft', 'Draft'), ('hr', 'HR Approval'), ('cfo', 'Finance Approval'),
                              ('paid', 'Paid')], default='draft', string='State')
    account_id = fields.Many2one('account.move', string='Invoice Ref', readonly=1)

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id, track_visibility='always')

    @api.multi
    def send_to_hr(self):
        if self.total_amount > self.employee_credit:
            raise ValidationError(_("Sorry, you don't have enough credit to process this"))
        self.name = self.env['ir.sequence'].next_by_code('medical.request')
        self.state = 'hr'

    @api.multi
    def draft(self):
        self.state = 'draft'

    @api.multi
    def send_to_cfo(self):
        self.state = 'cfo'

    @api.multi
    def paid(self):
        company_id = self.env.user.company_id
        if not company_id.bank_acc:
            raise UserError(_('You have not selected a Medical Limit Bank'))
        if not company_id.medical_bill_account:
            raise UserError(_('You have not selected a Medical Limit Bank'))

        acc_move_line = self.env['account.move.line'].with_context(check_move_validity=False)

        acc_move = self.env['account.move'].create({
            'journal_id': 1,
        })

        acc_move_line.create({
            'type': 'src',
            'name': 'Medical Bills',
            'quantity': 1,
            'credit': self.total_amount,
            'debit': 0.0,
            'account_id': company_id.bank_acc.id,
            'move_id': acc_move.id,
            'partner_id': self.employee_id.user_id.id

        })

        acc_move_line.create({
            'type': 'src',
            'name': 'Medical Bills',
            'quantity': 1,
            'debit': self.total_amount,
            'credit': 0.0,
            'account_id': company_id.medical_bill_account.id,
            'move_id': acc_move.id,
            'partner_id': self.employee_id.user_id.id
        })

        acc_move.post()
        self.account_id = acc_move.id
        self.employee_id.write({'medical_limit': self.employee_credit-self.total_amount})

        self.state = 'paid'


class MedicalDetails(models.Model):
    _name = 'medical.details.line'

    name = fields.Char(string='Medical Issue')
    description = fields.Text(string='Description')
    amount = fields.Float(string='Amount')
    medical_id = fields.Many2one('medical.request')
