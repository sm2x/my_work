# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PosInvoicing(models.Model):
    _name = "pos.invoicing"

    name = fields.Char('name')

    partner_id = fields.Many2one('res.partner', string='Customer')
    currency_id = fields.Many2one(related='partner_id.currency_id')

    # order_type = fields.Selection([
    #     ('bill', 'Vendor Bill'),
    #     ('invoice', 'Customer Invoice')], string='Invoice Type')

    order_state = fields.Selection([
        ('open', 'Open'), ('paid', 'Paid'), ('posted', 'Posted'), ], string='Order State')

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', 'sale')])

    order_line_ids = fields.One2many('order.invoice.line', 'order_invoice_id', string='Orders')
    # total = fields.Monetary("Total", compute='compute_total', currency_field='currency_id')
    upload_clicked = fields.Boolean()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid')], default='draft')

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('pos.invoicing.seq')
        })
        return super(PosInvoicing, self).create(vals)

    @api.multi
    def approve_payment(self):
        for rec in self:
            rec.state = 'approved'

    @api.multi
    def compute_total(self):
        for rec in self:
            amount_bg_tax = 0
            for inv in rec.payment_guarantee_line_ids:
                # round_curr = inv.invoice_id.currency_id.round
                # += inv.total_bg
                amount_bg_tax += inv.total_bg
                print('inv.total_bg', inv.total_bg)

            rec.total = amount_bg_tax

    @api.multi
    def upload_orders(self):
        for rec in self:
            orders = []
            if rec.order_line_ids:
                rec.order_line_ids.unlink()

            open_orders = rec.env['pos.order'].search([('partner_id', '=', rec.partner_id.id),
                                                       ('state', '=', 'open')])
            paid_orders = rec.env['pos.order'].search([('partner_id', '=', rec.partner_id.id),
                                                       ('state', '=', 'paid')])

            posted_orders = rec.env['pos.order'].search([('partner_id', '=', rec.partner_id.id),
                                                         ('state', '=', 'posted')])
            all_orders = rec.env['pos.order'].search([('partner_id', '=', rec.partner_id.id)])

            if rec.order_state == 'all':
                if not all_orders:
                    raise ValidationError('There is no orders for this Partner yet')

                for order in all_orders:
                    orders.append((0, 0, {
                        'order_id': order.id,

                    }))

            if rec.order_state == 'open':
                if not open_orders:
                    raise ValidationError('There is no open orders for this Partner')

                for order in open_orders:
                    orders.append((0, 0, {
                        'order_id': order.id,

                    }))

            if rec.order_state == 'paid':
                if not paid_orders:
                    raise ValidationError('There is no Paid orders for this Partner')

                for order in paid_orders:
                    orders.append((0, 0, {
                        'order_id': order.id,

                    }))
            if rec.order_state == 'posted':
                if not posted_orders:
                    raise ValidationError('There is no Posted orders for this Partner')

                for order in posted_orders:
                    orders.append((0, 0, {
                        'order_id': order.id,

                    }))

            rec.order_line_ids = orders

    @api.multi
    def create_invoice(self):
        for rec in self:
            invoice = self.env['account.invoice']
            invoice_lines = []
            today = datetime.today()

            for line in rec.order_line_ids:
                for order_line in line.order_id.lines:
                    invoice_lines.append((0, 0, {
                        'invoice_id': invoice.id,
                        'product_id': order_line.product_id.id,
                        'name': order_line.product_id.name,
                        'quantity': order_line.product_qty,
                        'uom_id': order_line.product_uom.id,
                        'price_unit': order_line.price_unit,
                        'price_subtotal': order_line.price_unit,
                        'account_id': order_line.product_id.property_account_expense_id.id,
                        'invoice_line_tax_ids': [(6, 0, [x.id for x in order_line.taxes_id])],
                    }))

            invoice_vals = {
                'partner_id': rec.partner_id.id,
                'currency_id': rec.currency_id.id,
                'journal_id': rec.journal_id.id,
                'date_invoice': today,
                'origin': rec.partner_id.name+'/Invoice',
                'type': 'out_invoice',
                'invoice_line_ids': invoice_lines,
            }
            invoice.create(invoice_vals)
            rec.upload_clicked = True

