# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions,_
from datetime import date, datetime, time, timedelta
from odoo.fields import Date, Datetime
from dateutil.relativedelta import relativedelta


class SalesTarget(models.Model):
    _name = 'target.sales'

    name = fields.Char('Target', required=True)
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)


class SalesTeamtarget(models.Model):
    _name = 'target.salesteam'

    name = fields.Many2one('target.sales', string='Target Name', required=True)
    user_ids = fields.Many2many('res.users', string='Sales Person')
    date_from = fields.Date(related ='name.date_from', string='Date From', )
    date_to = fields.Date(related ='name.date_to', string='Date To', )
    rule_ids = fields.One2many('target.rules', 'target_id', string='Sale & Invoice Target Rules',
                               help="Target Rules",
                               )
    payment_rule_ids = fields.One2many('payment.target.rules', 'target_id', string='Payment Target Rules',help="Payment Target Rules",)

    @api.model
    def create(self,vals):
        new_record = super(SalesTeamtarget, self).create(vals)
        return new_record

    @api.constrains('date_to','date_from')
    def _check_date_from_to(self):
        if self.date_from >= self.date_to:
            raise exceptions.ValidationError('Date from Must be less than Date to')

    @api.constrains('rule_ids')
    def _check_rule_ids(self):
        if self.rule_ids:
            for rec in self.rule_ids:
                categs = self.rule_ids.filtered(lambda x:x.categ_id == rec.categ_id)

                if len(categs)>1:
                    raise exceptions.ValidationError('Category Type %s cannot be repeated in rules'%categs[0].categ_id.name)
                if rec.sales_target<=0:
                    raise exceptions.ValidationError('Invalid Sale Amount %s'%rec.sales_target)
                if rec.commission_percent<=0:
                    raise exceptions.ValidationError('Invalid Target percentage %s'%rec.commission_percent)

        else:
            raise exceptions.ValidationError('Select Rules!')


class SalesInvoiceTargetRules(models.Model):
    _name = 'target.rules'
    target_id = fields.Many2one('target.salesteam', string='SaleTeam Target', )
    categ_id = fields.Many2one('product.category', 'Category Type',required=True)
    sales_target = fields.Float(string="Target Amount",required=True)
    quantity_target = fields.Float(string="Target Quantity",required=True)
    commission_percent = fields.Float(string="Commission Percent(%)",required=True)
    due_target_percent = fields.Float(string="Due Target Percent(%)",required=True,default=80)

    @api.constrains('commission_percent')
    def _check_commission_percent(self):
        for rule in self:
            if rule.commission_percent and rule.commission_percent <= 0.0:
                raise exceptions.ValidationError('Commission Percen Must Be > 0')
            if rule.commission_percent and rule.commission_percent >100:
                raise exceptions.ValidationError('Commission Percen Must Be<100')


class PaymentTargetRules(models.Model):
    _name = 'payment.target.rules'
    target_id = fields.Many2one('target.salesteam', string='SaleTeam Target', )
    sales_target = fields.Float(string="Sales Target",required=True)
    commission_percent = fields.Float(string="Commission Percent(%)",required=True)
    due_target_percent = fields.Float(string="Due Target Percent(%)",required=True,default=80)

    @api.constrains('commission_percent')
    def _check_commission_percent(self):
        for rule in self:
            if rule.commission_percent and rule.commission_percent <= 0.0:
                raise exceptions.ValidationError('Commission Percen Must Be > 0')
            if rule.commission_percent and rule.commission_percent >100:
                raise exceptions.ValidationError('Commission Percen Must Be<100')

