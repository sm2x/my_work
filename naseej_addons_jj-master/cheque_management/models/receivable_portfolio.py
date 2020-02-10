# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReceivablePortfolio(models.Model):
    _name = 'receivable.portfolio'
    _rec_name = 'receivable_sequence_id'

    receivable_sequence_id = fields.Char('Sequence', readonly=True)
    date = fields.Date("Issue Date")
    desc = fields.Text('Description')

    receiveACheque_ids = fields.One2many('receive.cheque2', 'receivablePortfolio_id', string='Cheques')
    post_checked = fields.Boolean('checked')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('receivable.seq') or '/'
        vals['receivable_sequence_id'] = seq
        return super(ReceivablePortfolio, self).create(vals)

    @api.multi
    def receive_cheques(self):
        self.post_checked = True
        for rec in self:
            for line in rec.receiveACheque_ids:
                line.receive_cheque()

