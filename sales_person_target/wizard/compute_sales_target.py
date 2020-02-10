# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class ComputeTarget(models.TransientModel):
    _name = "compute.sales.target"

    target_id = fields.Many2one('target.salesteam', 'Target')
    user_ids = fields.Many2many('res.users', string='Sales Persons')
    categ_ids = fields.Many2many('product.category', string='Category')
    start_date = fields.Date('Start Date', related='target_id.date_from')
    end_date = fields.Date('End Date', related='target_id.date_to')

    # sale_ok = fields.Boolean('Sales Orders')
    # invoice_ok = fields.Boolean('Invoices')
    payment_ok = fields.Boolean('Payments')
    # quantity_ok = fields.Boolean('Quantity')
    # amount_ok = fields.Boolean('Amount')

    type = fields.Selection(string="Based On", selection=[('sale', 'Sales Orders'), ('invoice', 'Invoices'), ])
    # ('payment', 'Payments'),
    computation_target = fields.Selection(string="Computation Target",
                                          selection=[('quantity', 'Quantity'), ('amount', 'Amount')])

    @api.onchange('type')
    def onchange_type(self):
        if self.type and self.type == 'payment':
            self.computation_target = 'amount'

    @api.onchange('target_id')
    def onchange_target_id(self):
        categ_ids = self.target_id.rule_ids.mapped('categ_id')
        # ('id', '=', self.target_id.rule_ids.categ_id.id),or
        #                                                          ('parent_id', '=', self.target_id.rule_ids.categ_id.id
        # categ_ids = self.env['product.category'].search([('id', '=', self.target_id.rule_ids.categ_id.id)]) and \
        #             self.env['product.category'].search([('parent_id', '=', self.target_id.rule_ids.categ_id.id)])
        user_ids = self.target_id.user_ids.ids
        self.user_ids = user_ids
        self.categ_ids = categ_ids
        return {
            'domain': {
                'user_ids': [('id', 'in', user_ids)],
                'categ_ids': [('id', 'in', categ_ids.ids)],
            }
        }

    # def compute_target(self):
    #     arr = []
    #     lazy_sales_person = self.env['res.users']
    #     if self.type == 'invoice':
    #         for user in self.user_ids:
    #             line_ids = []
    #
    #             for rule in self.target_id.rule_ids:
    #                 # TODO Ragaa Customization
    #                 # TODO lw menhom 2o parent lehom
    #                 if rule.categ_id in self.categ_ids:
    #                     amount_total_sales, quantity_total_sales = 0
    #
    #                     invoices = self.env['account.invoice'].search(
    #                         [('user_id', '=', user.id), ('date_invoice', '>=', self.start_date),
    #                          ('date_invoice', '<=', self.end_date), ('state', 'in', ['open', 'paid']),
    #                          ('type', '=', 'out_invoice')])
    #                     invoice_lines = self.env['account.invoice.line']
    #                     for invoice in invoices:
    #                         invoice_lines |= invoice.invoice_line_ids.filtered(
    #                             # TODO lw categ_id parent lehom (elmafrod kida bedawar gwa kol elly lehom parent bs)
    #                             lambda x: x.product_id.categ_id.parent_id.id == rule.categ_id.id)
    #
    #                         if self.amount_ok:
    #                             amount_total_sales = sum(x.price_subtotal for x in invoice_lines)
    #                             if rule.sales_target > 0:
    #                                 amount_percent = amount_total_sales / rule.sales_target * 100
    #                             else:
    #                                 amount_percent = 0
    #
    #                         if self.quantity_ok:
    #                             quantity_total_sales = sum(x.quantity for x in invoice_lines)
    #                             if rule.sales_target > 0:
    #                                 quantity_percent = quantity_total_sales / rule.quantity_target * 100
    #                             else:
    #                                 quantity_percent = 0
    #
    #                         if amount_total_sales or quantity_total_sales:
    #                             if amount_total_sales >= rule.sales_target or amount_percent >= rule.due_target_percent:
    #                                 if quantity_total_sales >= rule.quantity_target or quantity_percent >= rule.due_target_percent:
    #                                     line_ids.append((0, 0, {'categ_id': rule.categ_id.id,
    #                                                             'amount': amount_total_sales,
    #                                                             'amount_commission': rule.commission_percent / 100 * amount_total_sales,
    #                                                             'amount_commission_percent': amount_total_sales / rule.sales_target * 100,
    #                                                             'quantity_target': quantity_total_sales,
    #                                                             'qty_commission': rule.commission_percent / 100 * quantity_total_sales,
    #                                                             'qty_commission_percent': quantity_total_sales / rule.quantity_target * 100,
    #
    #                                                             }))
    #
    #                     if line_ids:
    #                         re = self.add_achieved_target(user, line_ids)
    #                         # if re:
    #                         #     re.write({'computation_target': self.computation_target})
    #                         arr.append(re.id)
    #                     else:
    #                         lazy_sales_person += user
    #     # self.type = 'invoice'
    #
    #     elif self.type == 'sale':
    #         for user in self.user_ids:
    #             line_ids = []
    #             for rule in self.target_id.rule_ids:
    #                 if rule.categ_id in self.categ_ids:
    #                     print('sale inner rule', rule.categ_id.name)
    #                     total_sales = 0
    #                     sales = self.env['sale.order'].search(
    #                         [('user_id', '=', user.id), ('date_order', '>=', self.start_date),
    #                          ('date_order', '<=', self.end_date), ('state', 'in', ['sale', 'done'])])
    #
    #                     order_lines = self.env['sale.order.line']
    #                     for sale in sales:
    #                         order_lines |= sale.order_line.filtered(
    #                             lambda x: x.product_id.categ_id.parent_id.id == rule.categ_id.id)
    #                         print(len(order_lines))
    #                         # print('product_id', order_lines.product_id.name,'categ_id', order_lines.product_id.categ_id.name)
    #                     if self.amount_ok:
    #                         total_sales = sum(x.price_subtotal for x in order_lines)
    #                         if rule.sales_target > 0:
    #                             percent = total_sales / rule.sales_target * 100
    #                         else:
    #                             percent = 0
    #                         print(total_sales, rule.sales_target)
    #                         if total_sales >= rule.sales_target or percent >= rule.due_target_percent:
    #                             line_ids.append((0, 0, {'categ_id': rule.categ_id.id,
    #                                                     'amount': total_sales,
    #                                                     'commission': rule.commission_percent / 100 * total_sales,
    #                                                     'commission_percent': total_sales / rule.sales_target * 100
    #                                                     }))
    #                         self.computation_target = 'amount'
    #                     if self.quantity_ok:
    #                         total_sales = sum(x.product_uom_qty for x in order_lines)
    #                         if rule.sales_target > 0:
    #                             percent = total_sales / rule.quantity_target * 100
    #                         else:
    #                             percent = 0
    #                         print(total_sales, rule.quantity_target)
    #                         if total_sales >= rule.quantity_target or percent >= rule.due_target_percent:
    #                             line_ids.append((0, 0, {'categ_id': rule.categ_id.id,
    #                                                     'quantity_target': total_sales,
    #                                                     'commission': rule.commission_percent / 100 * total_sales,
    #                                                     'commission_percent': total_sales / rule.quantity_target * 100
    #                                                     }))
    #                         self.computation_target = 'quantity'
    #
    #             if line_ids:
    #                 re = self.add_achieved_target(user, line_ids)
    #                 if re:
    #                     re.write({'computation_target': self.computation_target})
    #
    #                 arr.append(re.id)
    #             else:
    #                 lazy_sales_person += user
    #
    #         self.type = 'sale'
    #
    #     if self.payment_ok:
    #         print("True")
    #         for user in self.user_ids:
    #             print("sales_person", user.name)
    #             line_ids = []
    #             for rule in self.target_id.payment_rule_ids:
    #                 amount = 0
    #                 invoices = self.env['account.invoice'].search(
    #                     [('user_id', '=', user.id), ('date_invoice', '>=', self.start_date),
    #                      ('date_invoice', '<=', self.end_date), ('state', 'in', ['open', 'paid']),
    #                      ('type', '=', 'out_invoice')])
    #
    #                 print("invoices", invoices)
    #                 for invoice in invoices:
    #                     amount += invoice.amount_total-invoice.residual
    #
    #                 if rule.sales_target > 0:
    #                     percent = amount / rule.sales_target * 100
    #                 else:
    #                     percent = 0
    #                 print(amount)
    #                 if amount >= rule.sales_target or percent >= rule.due_target_percent:
    #                     line_ids.append((0, 0, {'amount': amount,
    #                                             'commission': rule.commission_percent / 100 * amount,
    #                                             'commission_percent': amount / rule.sales_target * 100
    #                                             }))
    #             self.computation_target = 'pay'
    #             if line_ids:
    #                 re = self.add_achieved_target(user, line_ids)
    #                 if re:
    #                     re.write({'computation_target': self.computation_target})
    #                 arr.append(re.id)
    #             else:
    #                 lazy_sales_person += user
    #
    #         self.type = 'payment'
    #     if arr:
    #         return {
    #             'domain': [('id', 'in', arr)],
    #             'name': 'Achieved Targets',
    #             'res_model': 'target.achieved',
    #             'view_type': 'form',
    #             'view_mode': 'tree,form',
    #             'type': 'ir.actions.act_window',
    #         }
    #     if lazy_sales_person:
    #         users_names = lazy_sales_person.mapped('name')
    #         print(users_names)
    #         raise exceptions.ValidationError('This Sales Persons {} Not Achieve There Targets !'.format(users_names))


def add_achieved_target(self, user, lines):
    old_t_id = self.check_old_achieved_target(user)
    if old_t_id:
        raise exceptions.ValidationError(
            'Sales Person {} already have achieved target for {} Based on {} \n'
            'Please Remove This Sales Person From Report And Try Again.\n'.format(user.name, self.target_id.name,
                                                                                  self.type))
    target_line_data = {
        'user_id': user.id,
        'target_id': self.target_id.id,
        'date_from': self.start_date,
        'type': self.type,
        'state': 'confirmed',
        'date_to': self.end_date,
        'line_ids': lines,

    }
    res = self.env['target.achieved'].create(target_line_data)
    return res


def check_old_achieved_target(self, user):
    old_achieved_target = self.env['target.achieved'].search([('user_id', '=', user.id),
                                                              ('type', '=', self.type),
                                                              ('target_id', '=', self.target_id.id),
                                                              ('date_from', '=', self.start_date),
                                                              ('date_to', '=', self.end_date),
                                                              ('state', '=', 'confirmed')])

    return old_achieved_target
