# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError
from odoo.fields import Date, Datetime
from datetime import date, datetime, time, timedelta
import time
from odoo import api, models, _
from odoo.exceptions import UserError


class SalespersonTargetCheck(models.TransientModel):
    _name = "salesperson.target.check"

    target_id = fields.Many2one('target.salesteam', 'Target')
    user_ids = fields.Many2many('res.users', string='Sales Persons')
    categ_ids = fields.Many2many('product.category', string='Category')
    start_date = fields.Date('Start Date', related='target_id.date_from')
    end_date = fields.Date('End Date', related='target_id.date_to')
    type = fields.Selection(string="Based On", selection=[('sale', 'Sales Orders'), ('invoice', 'Invoices'),
                                                          ('payment', 'Payments'), ],
                            required=True, default='sale')
    computation_target = fields.Selection(string="Computation Target",
                                          selection=[('quantity', 'Quantity'), ('amount', 'Amount')],
                                          required=True, default='quantity')

    @api.onchange('target_id')
    def onchange_target_id(self):
        categ_ids = self.target_id.rule_ids.mapped('categ_id')
        user_ids = self.target_id.user_ids.ids
        self.user_ids = user_ids
        self.categ_ids = categ_ids
        return {
            'domain': {
                'user_ids': [('id', 'in', user_ids)],
                'categ_ids': [('id', 'in', categ_ids.ids)],
            }
        }

    @api.onchange('type')
    def onchange_type(self):
        if self.type and self.type == 'payment':
            self.computation_target = 'amount'

    def print_report(self, data):
        data['form'] = {}
        data['form'].update({'report_id': self.id})
        return self.env.ref('sales_person_target.target_check_report').report_action(self, data=data)


class ReportJournal(models.AbstractModel):
    _name = 'report.sales_person_target.target_check_report_template'
    _description = 'Salesperson Target Check Report'

    def get_data(self, report, ):
        data = []
        if report.type == 'invoice':
            for user in report.user_ids:
                user_dic = {'user': user}
                rules = []
                for rule in report.target_id.rule_ids:
                    if rule.categ_id in report.categ_ids:
                        rule_dic = {'categ_id': rule.categ_id}
                        total_sales = 0
                        invoices = report.env['account.invoice'].search(
                            [('user_id', '=', user.id), ('date_invoice', '>=', report.start_date),
                             ('date_invoice', '<=', report.end_date), ('state', 'in', ['open', 'paid']),
                             ('type', '=', 'out_invoice')])
                        invoice_lines = self.env['account.invoice.line']
                        for invoice in invoices:
                            invoice_lines |= invoice.invoice_line_ids.filtered(
                                lambda x: x.product_id.categ_id.id == rule.categ_id.id)
                        res = None
                        if report.computation_target == 'quantity':
                            res = self.calc_target(invoice_lines=invoice_lines, rule=rule, type='quantity')
                        elif report.computation_target == 'amount':
                            res = self.calc_target(invoice_lines=invoice_lines, rule=rule, type='amount')
                        rule_dic.update(res)
                        rules.append(rule_dic)
                user_dic.update({'rules': rules})
                data.append(user_dic)

        elif report.type == 'sale':
            for user in report.user_ids:
                user_dic = {'user': user}
                rules = []
                for rule in report.target_id.rule_ids:
                    if rule.categ_id in report.categ_ids:
                        rule_dic = {'categ_id': rule.categ_id}
                        total_sales = 0
                        sales = self.env['sale.order'].search(
                            [('user_id', '=', user.id), ('date_order', '>=', report.start_date),
                             ('date_order', '<=', report.end_date), ('state', 'in', ['sale', 'done'])])

                        order_lines = self.env['sale.order.line']
                        for sale in sales:
                            order_lines |= sale.order_line.filtered(
                                lambda x: x.product_id.categ_id.id == rule.categ_id.id)
                        print(order_lines)
                        res = None
                        if report.computation_target == 'quantity':
                            res = self.calc_target(order_lines=order_lines, rule=rule, type='quantity')
                        elif report.computation_target == 'amount':
                            res = self.calc_target(order_lines=order_lines, rule=rule, type='amount')
                        rule_dic.update(res)
                        rules.append(rule_dic)
                user_dic.update({'rules': rules})
                data.append(user_dic)
        elif report.type == 'payment':
            for user in report.user_ids:
                user_dic = {'user': user}
                rules = []
                for rule in report.target_id.payment_rule_ids:
                    # if rule.categ_id in report.categ_ids:
                    # rule_dic = {'categ_id': rule.categ_id}
                    rule_dic = {}
                    amount = 0
                    invoices = self.env['account.invoice'].search(
                        [('user_id', '=', user.id), ('date_invoice', '>=', report.start_date),
                         ('date_invoice', '<=', report.end_date), ('state', 'in', ['open', 'paid']),
                         ('type', '=', 'out_invoice')])

                    print("invoices", invoices)
                    for invoice in invoices:
                        amount += invoice.amount_total - invoice.residual
                    percent = 0
                    if rule.sales_target > 0:
                        percent = amount / rule.sales_target * 100
                    remain = 0.0
                    remain_percent = 0.0
                    if amount < rule.sales_target:
                        remain = rule.sales_target - amount
                        remain_percent = remain / rule.sales_target * 100

                    rule_dic.update({'sale_target': rule.sales_target, 'total_sales': amount,
                                     'target_percent': rule.due_target_percent, 'current_percent': percent,
                                     'remain': remain, 'remain_percent': remain_percent})

                    rules.append(rule_dic)

                user_dic.update({'rules': rules})
                data.append(user_dic)
        return data

    def calc_target(self, order_lines=None, invoice_lines=None, rule=None, type=None):
        total_sales=0
        if type == 'amount':
            if order_lines:
                total_sales = sum(x.price_subtotal for x in order_lines)
            elif invoice_lines:
                total_sales = sum(x.price_subtotal for x in invoice_lines)

            print(total_sales)
            percent = 0.0
            if rule.sales_target > 0:
                percent = total_sales / rule.sales_target * 100

            remain = 0.0
            remain_percent = 0.0
            if total_sales < rule.sales_target:
                remain = rule.sales_target - total_sales
                remain_percent = remain / rule.sales_target * 100
            return {
                'sale_target': round(rule.sales_target, 2),
                'total_sales': round(total_sales, 2),
                'target_percent': round(rule.due_target_percent, 2),
                'current_percent': round(percent, 2),
                'remain': round(remain, 2),
                'remain_percent': round(remain_percent, 2)
            }
        elif type == 'quantity':
            total_qty = 0.0
            if order_lines:
                total_qty = sum(x.product_uom_qty for x in order_lines)
            elif invoice_lines:
                total_qty = sum(x.quantity for x in invoice_lines)
            percent = 0.0
            if rule.quantity_target > 0:
                percent = total_qty / rule.quantity_target * 100

            remain = 0.0
            remain_percent = 0.0
            if total_qty < rule.quantity_target:
                remain = rule.quantity_target - total_qty
                remain_percent = remain / rule.quantity_target * 100
            return {
                'sale_target': round(rule.quantity_target, 2),
                'total_sales': round(total_qty, 2),
                'target_percent': round(rule.due_target_percent, 2),
                'current_percent': round(percent, 2),
                'remain': round(remain, 2),
                'remain_percent': round(remain_percent, 2)
            }

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env['salesperson.target.check']
        report = model.browse(data['form'].get('report_id'))
        data = self.get_data(report)
        print(data)
        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': model.browse(docids),
            'data': data,
            'target': report.target_id,
            'date_from': report.start_date,
            'date_to': report.end_date,
            'type': report.type,
            'computation_target': report.computation_target,
        }
