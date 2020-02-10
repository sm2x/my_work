# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
# from odoo.tools import amount_to_text_en
from datetime import datetime, timedelta


class ChequeMaster(models.Model):
    _name = "cheque.master"
    _description = "Cheque Master Book"

    dates_ids = fields.One2many('dates.line', 'cheque_id', 'Tracking Dates')

    name = fields.Char(string='Cheque Ref', readonly=True)
    cheque_no = fields.Char(string='Cheque No.', readonly=True)
    bank_name = fields.Many2one('account.bank', string='Bank Name')
    cheque_date = fields.Date(string='Cheque Date')

    partner_id = fields.Many2one('res.partner', string="Issue To")
    partner_account_id = fields.Many2one('account.account', string="Partner Account")
    receiver_name = fields.Char(string='Receiver Name', readonly=True)
    designation = fields.Char(string='Receiver Designation', readonly=True)
    phone = fields.Char(string='Receiver Contact No.')
    cheque_date_issue = fields.Date(string='Cheque Issue Date')
    # account_move_ids = fields.Many2many('account.move', 'cheque_move_rel', 'cheque_id', 'move_id',
    #                                     'Related Accounting Entries', readonly=True)

    # CHANGES
    name_in_cheque = fields.Char(string="Name in Cheque")
    issue_journal_entry = fields.Many2one('account.move', 'Accounting Entry', readonly=True)
    dest_account_id = fields.Many2one('account.account', string="Destination Account")

    # DATES
    date_issue = fields.Date(string='Printed On', default=fields.Date.context_today)

    state = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
        ('printed', 'Printed'),
        ('issued', 'Issued'),
        ('hold', 'On Hold'),
        ('pending', 'Pending'),
        ('cleared', 'Cleared'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
        ('lost', 'Lost'),
    ], string='Status', readonly=True)
    comment = fields.Text(string="Comment")
    amount = fields.Float('Amount')

    amount_currency = fields.Monetary('Amount Currency', required=True, compute='compute_amount', readonly=True)

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.multi
    @api.depends('currency_id', 'amount', 'amount_currency')
    def compute_amount(self):
        for rec in self:
            company_id = rec.env.user.company_id
            rec.amount_currency = rec.amount
            rec.amount_currency = rec.currency_id._convert(rec.amount_currency, company_id.currency_id, company_id,
                                                           rec.date_issue or fields.Date.today())

    #####################################################################################################
    @api.onchange('date_issue')
    def _onchange_date_issue(self):
        if self.date_issue and not self.cheque_date:
            self.cheque_date = self.date_issue

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            self.name_in_cheque = self.partner_id.name
        if self.partner_id.customer:  #
            self.dest_account_id = self.partner_id.property_account_receivable_id
        elif self.partner_id.supplier:  #
            self.dest_account_id = self.partner_id.property_account_payable_id
        else:
            pass

    @api.model
    def create(self, vals):

        vals['state'] = 'new'

        return super(ChequeMaster, self).create(vals)

    @api.multi
    def post_cheque(self):
        if self.amount <= 0:
            raise UserError(_('Cheque amount must be greater than zero !!!'))

        cheque_config = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not cheque_config.cheque_journal_p_id:
            raise UserError(_('Set Cheque Payment Journal under Settings !!!'))

        journal_id = cheque_config.cheque_journal_p_id.id

        line_ids = [
            (0, 0, {'journal_id': journal_id,
                    'account_id': self.bank_name.pdc_account_id.id,
                    'name': self.name,
                    'amount_currency': -self.amount_currency or False,
                    'currency_id': self.currency_id.id,
                    'credit': self.amount}),

            (0, 0, {'journal_id': journal_id,
                    'account_id': self.dest_account_id.id,
                    'name': '/',
                    'amount_currency': self.amount_currency or False,
                    'currency_id': self.currency_id.id,
                    'debit': self.amount,
                    'partner_id': self.partner_id.id})
        ]
        vals = {

            'journal_id': journal_id,
            'ref': self.name,
            'date': self.date_issue,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        dates_lines = [
            (0, 0, {

                'cheque_state': 'Printed',
                'state_date': self.date_issue,
                'state_journal': account_move.id
            })]
        account_move.post()
        self.issue_journal_entry = account_move.id
        self.state = 'printed'
        self.write({'state': 'printed',
                    'cheque_date': self.cheque_date,
                    # 'account_move_ids': [(4, account_move.id)],
                    'partner_id': self.partner_id.id,
                    'partner_account_id': self.dest_account_id.id,
                    'amount': self.amount,
                    'dates_ids': dates_lines})

    @api.multi
    def lost_cheque(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lost Cheque',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'lost.cheque',
            'target': 'new',
            'context': 'None'
        }

    # create journal??
    @api.multi
    def _check_pending(self):
        today = fields.Date.context_today(self)
        today_date = datetime.strptime(today, '%Y-%m-%d').date()
        dates_lines = [
            (0, 0, {
                'cheque_state': 'Pending',
                'state_date': today_date,
            })]
        cheques = ""
        for record in self.search([('state', 'in', ('issued', 'hold'))]):
            if record.cheque_date < today and record.state == 'issued':
                record.write({'state': 'pending',
                              'dates_ids': dates_lines})

            elif record.state == 'hold' and record.hold_date < today:
                record.write({'state': 'pending',
                              'dates_ids': dates_lines})
        config_obj = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        alert_days = config_obj.alert_outbound
        alert_date = today_date+timedelta(days=alert_days)
        alert_cheques = []
        for record in self.search([('state', 'in', ('issued', 'hold'))]):
            if record.cheque_date == str(alert_date) and record.state == 'issued':
                cheques = cheques+record.name+", "
                alert_cheques.append(record)
            elif record.state == 'hold' and record.hold_date == str(alert_date):
                cheques = cheques+record.name+", "
                alert_cheques.append(record)

        if cheques != "":
            cheques = cheques[:-2]
            cheques = cheques+"\n"
            conf = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
            vals = {'state': 'outgoing',
                    'subject': 'Outbound Cheques Pending List',
                    'body_html': """<div>
                                        <p>Hello,</p>
                                        <p>This is a system generated reminder mail. The following outbound cheques are pending.</p>
                                    </div>
                                    <blockquote>%s</blockquote>
                                    <div>Thank You</div>""" % (cheques),
                    'email_to': conf.email,
                    }
            email_id = self.env['mail.mail'].create(vals)
            email_id.send()

    # create journal??
    @api.multi
    def immediate_make_pending(self):
        for record in self.search([]):
            record.make_pending()

    # create journal??

    @api.multi
    def make_pending(self):
        today = fields.Date.context_today(self)
        dates_lines = [
            (0, 0, {
                'cheque_state': 'Pending',
                'state_date': today,
            })]
        if self.cheque_date < today and self.state == 'issued':
            self.write({'state': 'pending',
                        'dates_ids': dates_lines})
        elif self.state == 'hold' and self.hold_date < today:
            self.write({'state': 'pending',
                        'dates_ids': dates_lines})

    @api.multi
    def print_cheque(self):
        today = fields.Date.context_today(self)
        dates_lines = [
            (0, 0, {
                'cheque_state': 'Cheque Printed',
                'state_date': today,
            })]
        self.write({'dates_ids': dates_lines})
        return self.env.ref('payment_in_cheque.report_cheque_payment').report_action(self)

    @api.multi
    def amount_to_text(self, amount):
        # convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        # convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        # return convert_amount_in_words
        return self.env.user.currency_id.amount_to_text(amount)

    # create journal??
    @api.multi
    def issue_cheque(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Issue Cheque',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'issue.cheque.wizard',
            'target': 'new',
            'context': 'None'
        }

    # create journal??
    @api.multi
    def clear_cheque(self):
        view = self.env.ref('payment_in_cheque.wizard_clear_cheque')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cheque Clearance',
            'view_id': view.id,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'clear.cheque',
            'target': 'new',
            'context': 'None'
        }

    # create journal??
    @api.multi
    def hold_cheque(self):
        view = self.env.ref('payment_in_cheque.wizard_clear_cheque3')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cheque Hold',
            'view_id': view.id,
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'clear.cheque',
            'target': 'new',
            'context': 'None'
        }

    # create journal??
    @api.multi
    def cancel_cheque(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cheque Cancellation',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'cancel.cheque',
            'target': 'new',
            'context': 'None'
        }

    # create journal??
    @api.multi
    def return_cheque(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cheque Return',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'return.cheque',
            'target': 'new',
            'context': 'None'
        }
