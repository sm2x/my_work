# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DishonourCheque(models.TransientModel):
    _name = "dishonour.cheque"

    present_date = fields.Date(string='Cheque Present Date', default=fields.Date.context_today, required=True)
    date_return = fields.Date(string='Cheque Return Date', default=fields.Date.context_today, required=True)
    charge = fields.Float('Service Charges if any')
    charge_currency = fields.Monetary('charge Currency', required=True, compute='compute_charge')

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.multi
    @api.depends('currency_id', 'charge', 'charge_currency')
    def compute_charge(self):
        for rec in self:
            company_id = rec.env.user.company_id
            rec.charge_currency = rec.charge
            rec.charge_currency = rec.currency_id._convert(rec.charge_currency, company_id.currency_id, company_id,
                                                           rec.date_return or fields.Date.today())

    @api.multi
    def dishonour_cheque(self):
        cheque_obj = self.env['receive.cheque.master'].browse(self.env.context.get('active_id'))
        cheque_config = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not cheque_config.cheque_journal_r_id:
            raise UserError(_('Set Cheque Receipt Journal under Settings !!!'))
        journal_id = cheque_config.cheque_journal_r_id.id
        interim_account = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
        if not interim_account.interim_account_id:
            raise UserError('Set Customer Cheque Interim Account under Settings !!!')
        line_ids = []


        if self.charge and self.charge > 0:
            line_ids = [(0, 0,
                         {'journal_id': journal_id,
                          'account_id': cheque_obj.bank_id.account_id.id,
                          'name': '/',
                          'amount_currency': -self.charge_currency or False,
                          'currency_id': self.currency_id.id,
                          'credit': self.charge}),


                        (0, 0, {'journal_id': journal_id,
                                'account_id': interim_account.charges_account_id.id,
                                'partner_id': cheque_obj.partner_id.id,
                                'name': 'Bank Charges',
                                'amount_currency': self.charge_currency or False,
                                'currency_id': self.currency_id.id,
                                'debit': self.charge})]
        line_ids.extend([(0, 0,
                          {'journal_id': journal_id,
                           'account_id': cheque_obj.bank_id.deposit_account.id,
                           'name': '/',
                           'amount_currency': -self.charge_currency or False,
                           'currency_id': self.currency_id.id,
                           'credit': cheque_obj.amount}),

                         (0, 0, {'journal_id': journal_id,
                                 'account_id': interim_account.interim_account_id.id,
                                 'partner_id': cheque_obj.partner_id.id,
                                 'name': cheque_obj.name,
                                 'amount_currency': self.charge_currency or False,
                                 'currency_id': self.currency_id.id,
                                 'debit': cheque_obj.amount}),
                         ])
        vals = {
            'journal_id': journal_id,
            'ref': cheque_obj.name,
            'date': self.date_return,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        cheque_obj.write({'state': 'dishonoured',
                          'present_date': self.present_date,
                          'date_return': self.date_return,
                          'account_move_ids': [(4, account_move.id)],})
