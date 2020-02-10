# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime


class SalesTargetAchieved(models.Model):
    _name = 'target.achieved'
    _rec_name = 'user_id'

    user_id = fields.Many2one('res.users', string='Sales Person',
                              help="sales person associated with this target",
                              required=True)
    target_id = fields.Many2one('target.salesteam', string='Target',
                                help="Related Target", )
    date_from = fields.Date('Date From', )
    date_to = fields.Date('Date To', )
    line_ids = fields.One2many(comodel_name="target.achieved.lines", inverse_name="achieved_id", string="",
                               required=False, )
    state = fields.Selection(string="Status",
                             selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled'), ],
                             required=False, default='draft')
    type = fields.Selection(string="Based On", selection=[('sale', 'Sales Orders'), ('invoice', 'Invoices'),
                                                          ('payment', 'Payments'), ], required=True, )
    computation_target = fields.Selection(string="Computation Target",
                                          selection=[('quantity', 'Quantity'), ('amount', 'Amount')],
                                          required=False)

    def action_cancel(self):
        self.state = 'canceled'


class SalesTargetAchievedLines(models.Model):
    _name = 'target.achieved.lines'
    achieved_id = fields.Many2one('target.achieved')
    amount = fields.Float(string="Amount")
    amount_commission = fields.Float(string="Amount Commission")
    qty_commission = fields.Float(string="Quantity Commission")
    categ_id = fields.Many2one('product.category', 'Category')
    amount_commission_percent = fields.Float('Amount Percent(%)')
    qty_commission_percent = fields.Float('Quantity Percent(%)')
    quantity_target = fields.Float(string="Quantity")
