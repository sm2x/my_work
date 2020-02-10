# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
from num2words import num2words

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('leader_approved', 'Leader Approved'),
    ('manager_approved', 'Manager Approved'),
    ('rejected', 'Rejected'),
    ('done', 'Done')
]


class SprogroupPurchaseRequest(models.Model):
    _name = 'sprogroup.purchase.request'
    _description = 'Sprogroup Purchase Request'
    _inherit = ['mail.thread']

    # @api.constrains('line_ids.product_id', 'line_ids.supplier_id')
    # def _check_supplier_id(self):
    #     for line in self.line_ids:
    #         if not line.product_id:
    #             raise ValidationError(_('Please select a product.'))
    #         if not line.supplier_id:
    #             raise ValidationError(_('Please select a vendor.'))

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('sprogroup.purchase.request')

    name = fields.Char('Request Name', size=32, required=True, track_visibility='onchange')
    code = fields.Char('Code', size=32, required=True, default=_get_default_name, track_visibility='onchange')
    date_start = fields.Date('Start date',
                             help="Date when the user initiated the request.",
                             default=fields.Date.context_today,
                             track_visibility='onchange')
    end_start = fields.Date('End date', default=fields.Date.context_today,
                            track_visibility='onchange')
    categ_id = fields.Many2one('product.category', string='Product Category')
    requested_by = fields.Many2one('res.users',
                                   'Requested by',
                                   required=True,
                                   track_visibility='onchange',
                                   default=_get_default_requested_by)
    location_id = fields.Many2one('stock.location', string='Location')

    company_id = fields.Many2one('res.company', related='requested_by.company_id', string='Company')

    assigned_to = fields.Many2one('res.users', 'Approver', required=True,
                                  track_visibility='onchange', compute='_compute_department')
    description = fields.Text('Description')

    line_ids = fields.One2many('sprogroup.purchase.request.line', 'request_id',
                               'Products to Purchase',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')
    req_type = fields.Selection(selection=[('argent', 'طارئ'), ('normal', 'عادى')],
                                string='Request Type',
                                index=True,
                                track_visibility='onchange',
                                copy=False, )
    rfq_clicked = fields.Boolean(copy=False)

    # @api.onchange('state')
    # def onchange_state(self):
    #     assigned_to = None
    #     if self.state:
    #         if (self.requested_by.id == False):
    #             self.assigned_to = None
    #             return
    #
    #         employee = self.env['hr.employee'].search([('work_email', '=', self.requested_by.email)])
    #         if (len(employee) > 0):
    #             if (employee[0].department_id and employee[0].department_id.manager_id):
    #                 assigned_to = employee[0].department_id.manager_id.user_id
    #
    #     self.assigned_to = assigned_to

    @api.multi
    @api.depends('requested_by')
    def _compute_department(self):
        for rec in self:
            if (rec.requested_by.id == False):
                rec.department_id = None
                return

            employee = rec.env['hr.employee'].search([('user_id', '=', rec.requested_by.id)])
            print(len(employee))
            if (len(employee) > 0):
                rec.department_id = employee[0].department_id
                rec.assigned_to = rec.department_id.manager_id.user_id
            else:
                rec.department_id = None
                rec.assigned_to = None

    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department')

    @api.one
    @api.depends('state')
    def _compute_can_leader_approved(self):
        current_user_id = self.env.uid
        if (self.state == 'to_approve' and current_user_id == self.assigned_to.id):
            self.can_leader_approved = True
        else:
            self.can_leader_approved = False

    can_leader_approved = fields.Boolean(string='Can Leader approved', compute='_compute_can_leader_approved')

    @api.one
    @api.depends('state')
    def _compute_can_manager_approved(self):
        current_user = self.env['res.users'].browse(self.env.uid)

        if (self.state == 'leader_approved' and current_user.has_group(
                'sprogroup_purchase_request.group_sprogroup_purchase_request_manager')):
            self.can_manager_approved = True
        else:
            self.can_manager_approved = False

    can_manager_approved = fields.Boolean(string='Can Manager approved', compute='_compute_can_manager_approved')

    @api.one
    @api.depends('state')
    def _compute_can_reject(self):
        self.can_reject = (self.can_leader_approved or self.can_manager_approved)

    can_reject = fields.Boolean(string='Can reject', compute='_compute_can_reject')

    @api.multi
    @api.depends('state')
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ('to_approve', 'leader_approved', 'manager_approved', 'rejected', 'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    is_editable = fields.Boolean(string="Is editable",
                                 compute="_compute_is_editable",
                                 readonly=True)

    @api.model
    def create(self, vals):
        request = super(SprogroupPurchaseRequest, self).create(vals)
        lines = self.line_ids.search([('request_id', '=', self.id)])
        for lineb in lines:
            print('lineb', lineb.product_id.name)
        products = lines.mapped('product_id')
        for product in products:
            print('products', product.name)

        for line in self.line_ids:
            print('in for')
            if line.product_id in products:
                print('in if')
                raise ValidationError(_('this product is already selected.'))

        if vals.get('assigned_to'):
            request.message_subscribe(partner_ids=[request.assigned_to.partner_id.id])
        return request

    @api.multi
    def write(self, vals):
        res = super(SprogroupPurchaseRequest, self).write(vals)
        for request in self:
            if vals.get('assigned_to'):
                self.message_subscribe(partner_ids=[request.assigned_to.partner_id.id])
        return res

    @api.multi
    def button_draft(self):
        self.mapped('line_ids').do_uncancel()
        return self.write({'state': 'draft'})

    @api.multi
    def button_to_approve(self):
        return self.write({'state': 'to_approve'})

    @api.multi
    def button_leader_approved(self):
        return self.write({'state': 'leader_approved'})

    @api.multi
    def button_manager_approved(self):
        return self.write({'state': 'manager_approved'})

    @api.multi
    def button_rejected(self):
        self.mapped('line_ids').do_cancel()
        return self.write({'state': 'rejected'})

    @api.multi
    def button_done(self):
        return self.write({'state': 'done'})

    @api.multi
    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({'state': 'rejected'})

    # @api.multi
    # def make_purchase_quotation(self):
    #     view_id = self.env.ref('purchase.purchase_order_form')
    #
    #     # vals = {
    #     #     'partner_id': partner.id,
    #     #     'picking_type_id': self.rule_id.picking_type_id.id,
    #     #     'company_id': self.company_id.id,
    #     #     'currency_id': partner.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id,
    #     #     'dest_address_id': self.partner_dest_id.id,
    #     #     'origin': self.origin,
    #     #     'payment_term_id': partner.property_supplier_payment_term_id.id,
    #     #     'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    #     #     'fiscal_position_id': fpos,
    #     #     'group_id': group
    #     # }
    #
    #     order_line = []
    #     for line in self.line_ids:
    #         product = line.product_id
    #         fpos = self.env['account.fiscal.position']
    #         if self.env.uid == SUPERUSER_ID:
    #             company_id = self.env.user.company_id.id
    #             taxes_id = fpos.map_tax(
    #                 line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
    #         else:
    #             taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id)
    #
    #         product_line = (0, 0, {'product_id': line.product_id.id,
    #                                'state': 'draft',
    #                                'product_uom': line.product_id.uom_po_id.id,
    #                                'price_unit': 0,
    #                                'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    #                                # 'taxes_id' : ((6,0,[taxes_id.id])),
    #                                'product_qty': line.product_qty,
    #                                'name': line.product_id.name
    #                                })
    #         order_line.append(product_line)
    #
    #     # vals = {
    #     #     'order_line' : order_line
    #     # }
    #     #
    #     # po = self.env['purchase.order'].create(vals)
    #
    #     return {
    #         'name': _('New Quotation'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'purchase.order',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'view_id': view_id.id,
    #         'views': [(view_id.id, 'form')],
    #         'context': {
    #             'default_order_line': order_line,
    #             'default_state': 'draft',
    #
    #         }
    #     }

    @api.onchange('line_ids')
    def check_product(self):
        print('in def')
        for rec in self:

            lines = rec.line_ids.search([('request_id', '=', rec.id)])
            for lineb in lines:
                print('lineb', lineb.product_id.name)
            products = lines.mapped('product_id')
            for product in products:
                print('products', product.name)

            for line in rec.line_ids:
                print('in for')
                if line.product_id in products:
                    print('in if')
                    raise ValidationError(_('this product is already selected.'))

    @api.multi
    def create_rfq(self):
        for rec in self:
            vendors = rec.line_ids.mapped('supplier_id')
            for vend in vendors:
                # print('vendor', vend.name)
                vend_lines = rec.line_ids.search([('supplier_id', '=', vend.id), ('request_id', '=', rec.id)])
                order_line = []
                for line in vend_lines:
                    # print('product', line.product_id.name)
                    fpos = self.env['account.fiscal.position']
                    if self.env.uid == SUPERUSER_ID:
                        company_id = self.env.user.company_id.id
                        taxes_id = fpos.map_tax(
                            line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
                    else:
                        taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id)

                    product_line = (0, 0, {'product_id': line.product_id.id,
                                           'state': 'draft',
                                           'product_uom': line.product_id.uom_po_id.id,
                                           'price_unit': 0,
                                           'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                           # 'taxes_id' : ((6,0,[taxes_id.id])),
                                           'product_qty': line.product_qty,
                                           'name': line.product_id.name
                                           })
                    order_line.append(product_line)

                vals = {
                    'partner_id': vend.id,
                    'company_id': rec.company_id.id,
                    'state': 'draft',
                    'order_line': order_line
                }
                rec.rfq_clicked = True
                rec.env['purchase.order'].create(vals)


class SprogroupPurchaseRequestLine(models.Model):
    _name = "sprogroup.purchase.request.line"
    _description = "Sprogroup Purchase Request Line"
    _inherit = ['mail.thread']

    # @api.multi
    # @api.depends('product_id', 'name', 'product_uom_id', 'product_qty',
    #              'date_required', 'specifications')
    # @api.multi
    # def _compute_supplier_id(self):
    #     for rec in self:
    #         if rec.product_id:
    #             if rec.product_id.seller_ids:
    #                 rec.supplier_id = rcategory_idec.product_id.seller_ids[0].name

    # domain = ['|', ('purchase_ok', '=', True)],

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    category_id = fields.Many2one('product.category', string='Product Category', compute='get_category')
    # domain = "[('purchase_ok', '=', True),'|', ('categ_id', '=', category_id), ('categ_id.parent_id', '=', category_id)]"
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain="['|', '&',('categ_id', '=', category_id), ('categ_id.parent_id', '=', category_id),('purchase_ok', '=', True)]",
        track_visibility='onchange')
    name = fields.Char('Description', size=256,
                       track_visibility='onchange')
    product_uom_id = fields.Many2one('product.uom', 'Product Unit of Measure',
                                     track_visibility='onchange')
    product_qty = fields.Float(string='Quantity', track_visibility='onchange',
                               digits=dp.get_precision('Product Unit of Measure'))
    request_id = fields.Many2one('sprogroup.purchase.request',
                                 'Purchase Request',
                                 ondelete='cascade', readonly=True)
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 store=True, readonly=True)
    product_stock_qty = fields.Float(compute='_compute_product_stock_qty')

    requested_by = fields.Many2one('res.users',
                                   related='request_id.requested_by',
                                   string='Requested by',
                                   store=True, readonly=True)
    assigned_to = fields.Many2one('res.users',
                                  related='request_id.assigned_to',
                                  string='Assigned to',
                                  store=True, readonly=True)
    date_start = fields.Date(related='request_id.date_start',
                             string='Request Date', readonly=True,
                             store=True)
    end_start = fields.Date(related='request_id.end_start',
                            string='End Date', readonly=True,
                            store=True)
    description = fields.Text(related='request_id.description',
                              string='Description', readonly=True,
                              store=True)
    date_required = fields.Date(string='Request Date',
                                track_visibility='onchange',
                                default=fields.Date.context_today)

    specifications = fields.Text(string='Specifications')
    request_state = fields.Selection(string='Request state',
                                     readonly=True,
                                     related='request_id.state',
                                     selection=_STATES,
                                     store=True)
    supplier_id = fields.Many2one('res.partner',
                                  string='Preferred supplier')

    cancelled = fields.Boolean(
        string="Cancelled", readonly=True, default=False, copy=False)
    #
    # @api.multi
    # def _compute_product_stock_qty(self):
    #     for rec in self:
    #         if rec.request_id.location_id:
    #             print('in if')
    #             quant_object = rec.env['stock.quant'].search(
    #                 [('product_id', '=', rec.product_id.id), ('location_id', '=', rec.request_id.location_id.id)])
    #             print(quant_object.quantity)
    #             rec.product_stock_qty = quant_object.quantity

    @api.multi
    @api.depends('request_id')
    def get_category(self):
        for rec in self:
            rec.category_id = rec.request_id.categ_id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n'+self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name

    @api.multi
    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({'cancelled': True})

    @api.multi
    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({'cancelled': False})

    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ('to_approve', 'leader_approved', 'manager_approved', 'rejected',
                                        'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    is_editable = fields.Boolean(string='Is editable',
                                 compute="_compute_is_editable",
                                 readonly=True)

    @api.multi
    def write(self, vals):
        res = super(SprogroupPurchaseRequestLine, self).write(vals)
        if vals.get('cancelled'):
            requests = self.mapped('request_id')
            requests.check_auto_reject()
        return res
