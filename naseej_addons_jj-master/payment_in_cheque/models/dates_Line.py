# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class DatesLine(models.Model):
    _name = "dates.line"

    cheque_id= fields.Many2one('cheque.master')

    cheque_state= fields.Char('State')
    state_date= fields.Date('State Date')
    state_journal = fields.Many2one('account.move')

