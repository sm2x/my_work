# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PaymentPortfolio(models.Model):
    _name = 'payment.portfolio'
    _rec_name = 'IssueCheque_ids'
    Payment_sequence_id = fields.Char('Sequence', readonly=True)
    date = fields.Date("Issue Date")
    # partner_id = fields.Many2one('res.partner', string="Receiving From", required=True)
    desc = fields.Text('Description')

    IssueCheque_ids = fields.One2many('issue.cheque', 'PaymentPortfolio_id', string='Cheques')
    post_checked = fields.Boolean('checked')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('Payment.seq') or '/'
        vals['Payment_sequence_id'] = seq
        return super(PaymentPortfolio, self).create(vals)

    @api.multi
    def post_cheques(self):
        self.post_checked = True
        for rec in self:
            for line in rec.IssueCheque_ids:
                line.post_cheque()

