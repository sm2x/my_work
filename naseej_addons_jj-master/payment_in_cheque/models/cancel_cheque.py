# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class CancelCheque(models.TransientModel):
    _name = "cancel.cheque"

    comment = fields.Text(string="Comment", required=True)
    date_cancel = fields.Date(string='Cancel Date', default=fields.Date.context_today, required=True)

    @api.multi
    def cancel_cheque(self):
        cheque_obj = self.env['cheque.master'].browse(self.env.context.get('active_id'))
        if cheque_obj.state == 'used':
            cheque_obj.write({'comment': self.comment, 'state': 'cancelled'})
        else:
            cheque_config = self.env['cheque.config.settings'].search([], order='id desc', limit=1)
            if not cheque_config.cheque_journal_p_id:
                raise UserError(_('Set Cheque Payment Journal under Settings !!!'))
            journal_id = cheque_config.cheque_journal_p_id.id
            line_ids = [
                (0, 0,
                 {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.pdc_account_id.id,
                  'name': cheque_obj.name,
                  'amount_currency': cheque_obj.amount_currency or False,
                  'currency_id': cheque_obj.currency_id.id,
                  'debit': cheque_obj.amount}),

                (0, 0, {'journal_id': journal_id,
                        'account_id': cheque_obj.partner_account_id.id,
                        'name': '/',
                        'amount_currency': -cheque_obj.amount_currency or False,
                        'currency_id': cheque_obj.currency_id.id,
                        'credit': cheque_obj.amount,
                        'partner_id': cheque_obj.partner_id.id})
            ]

            vals = {

                'journal_id': journal_id,
                'ref': cheque_obj.name,
                'date': self.date_cancel,
                'line_ids': line_ids,
            }
            account_move = self.env['account.move'].create(vals)
            dates_lines = [
                (0, 0, {
                    'cheque_state': 'Cancelled',
                    'state_date': self.date_cancel,
                    'state_journal': account_move.id
                })]
            account_move.post()
            cheque_obj.write({'state': 'cancelled',
                              'comment': self.comment,
                              'dates_ids': dates_lines})
