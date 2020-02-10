# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
import  datetime


class stock_quantity_inherite(models.Model):
    _inherit = 'stock.quant'

    product_category_id = fields.Many2one('product.category')

class pharma_jet_purshase_inventory(models.Model):
    # _inherit = 'purchase.order'
    _name = 'purchase.planning'

    dates = fields.Datetime(default= datetime.datetime.today())
    name = fields.Char(string='Code', index=True, readonly=True)
    date_from = fields.Datetime(string='Date From', required=True)
    date_to = fields.Datetime(string='Date To', required=True)
    internal_stock = fields.Many2many('stock.location',  default = lambda self: self._default_get())
    # , 'internal_stock_id'
    product_category = fields.Many2one('product.category', string='Product Category')
    state = fields.Selection(string="Status",
                             selection=[('draft', 'Draft'), ('waiting_approve', 'Waiting Approve'),
                                        ('approved', 'Approved'), ('done', 'Done'), ('cancel', 'Canceld')],
                             default='draft')

    relation_fiel = fields.One2many('purchase.planning_bridge', 'bridge_rel')

    @api.model
    def _default_get(self):
        return self.env['stock.location'].search([('location_id', '=', self.id) and ('usage', '=', 'internal')]).ids

    @api.model
    def create(self, vals):
        # serial_for_purchase_planning => this act id for view
        # generate_seq => this act field name
        # pharma_jet_purshase_inventory => module name

        sequence = self.env['ir.sequence'].next_by_code('serial_for_purchase_planning_code')
        vals['name'] = sequence
        result = super(pharma_jet_purshase_inventory, self).create(vals)
        # print(result)
        return result

    @api.multi
    def waiting_approve_request(self):
        self.state = 'waiting_approve'
    @api.multi
    def approved_request(self):
        self.state = 'approved'
    @api.multi
    def done_request(self):
        self.state = 'done'
    @api.multi
    def cancaled_request(self):
        self.state = 'cancel'

    @api.multi
    def generate_po(self):
        vendors = {}
        purchase_order = self.env['purchase.order']
        for rec in self:
                for vendor in rec.relation_fiel.mapped('vend_id'):
                    vendors[vendor.id] = rec.relation_fiel.filtered(lambda line: line.vend_id == vendor)
                l = []
                for i in rec.relation_fiel.mapped('prod_id'):
                    v = rec.relation_fiel.filtered(lambda l: l.prod_id == i)
                    qty = sum(v.mapped('demand_qty'))
                    l.append(qty)
                for vendor in vendors.keys():
                    line_ids = []
                    for line in vendors[vendor]:
                        line_ids.append((0, 0, {
                            'product_id': line.prod_id.id,
                            'name': line.prod_id.name,
                            'date_planned': line.generate_date,
                            'initial_qty': line.demand_qty,
                            'product_uom': line.product_uom_inherite.id,
                            'price_unit': line.last_price_po
                        }))
                    po_vals = {
                        'partner_id': vendor,
                        'date_order': fields.Datetime.now(),
                        'order_line': line_ids
                    }
                    t = po_vals
                    if line.go_po == True:
                        purchase_order.create(t)

    @api.multi
    def create_records(self):
        lines = []
        for rec in self:
            rec.relation_fiel.unlink()
            for stock in rec.internal_stock:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                for obj in stock_obj:
                    sold = stock.env['sale.order.line'].search([('product_id', '=', obj.product_id.id)])
                    pos_sold = stock.env['pos.order.line'].search([('product_id', '=', obj.product_id.id)])
                    pos_qty = 0
                    for line in pos_sold:
                        pos_qty = pos_qty + line.qty
                    qty = 0
                    for line in sold:
                        qty = qty + line.qty_delivered
                    vend = ''
                    for line in obj.product_id.seller_ids:
                        vend = line.name
                    po_obj = stock.env['purchase.order'].search([('product_id', '=', obj.product_id.id)],
                                                                limit=1)
                    last_po = po_obj.name
                    po_date = stock.env['purchase.order'].search([('product_id', '=', obj.product_id.id)],
                                                                 limit=1)
                    po_date_obj = po_date.date_order
                    po_received = stock.env['purchase.order.line'].search(
                        [('product_id', '=', obj.product_id.id)], limit=1)
                    po_qty_received = po_received.qty_received
                    po_last_price = po_received.price_unit
                    concat_stock = str(obj.location_id.location_id.name) + '/' + obj.location_id.name

                    for x in sold:
                        if x.qty_delivered:
                            rec.dates = x.order_id.confirmation_date

                    if rec.product_category:
                        if (obj.product_id.categ_id.name == rec.product_category.name):
                            lines.append({
                            'stock' : concat_stock,
                            'prod_id': obj.product_id.id,
                            'product_uom_inherite': po_received.product_uom,
                            'current_balance': obj.quantity,
                            'last_po_quantity': po_qty_received,
                            'last_price_po': po_last_price,
                            'vend_id': vend,
                            'pos_salable_quantity': pos_qty,
                            'salable_quantity': qty,
                            'quantity': (qty + pos_qty) - obj.quantity,
                            'demand_qty': (qty + pos_qty) - obj.quantity,
                            'last_po_num': last_po,
                            'last_po_date': po_date_obj
                        })
                    elif (rec.date_to >= rec.dates >= rec.date_from):
                        lines.append({
                            'stock': concat_stock,
                            'prod_id': obj.product_id.id,
                            'product_uom_inherite': po_received.product_uom,
                            'current_balance': obj.quantity,
                            'last_po_quantity': po_qty_received,
                            'last_price_po': po_last_price,
                            'vend_id': vend,
                            'pos_salable_quantity': pos_qty,
                            'salable_quantity': qty,
                            'quantity': (qty + pos_qty) - obj.quantity,
                            'demand_qty': (qty + pos_qty) - obj.quantity,
                            'last_po_num': last_po,
                            'last_po_date': po_date_obj
                        })
            rec.relation_fiel = lines
        return lines

class pharma_jet_purshase_inventory_bridge(models.Model):
    _name = 'purchase.planning_bridge'

    loc_id = fields.Many2many('stock.location')
    quantity = fields.Integer(string='Recommended Qty ', readonly=True)
    demand_qty = fields.Integer(string='Demand Qty')
    last_price_po = fields.Integer(string='Last Price P.O',readonly=True)
    last_po_quantity = fields.Integer(string='Last P.O Qty',readonly=True)
    last_po_num = fields.Char(string='Last P.O Number',readonly=True)
    salable_quantity = fields.Integer(string='Sales Sold Qty',readonly=True)
    pos_salable_quantity = fields.Integer(string='Pos Sold Qty',readonly=True)
    current_balance = fields.Integer(string='Current Balance', readonly=True)
    last_po_date = fields.Datetime(string='Last P.O Date',readonly=True)
    prod_id = fields.Many2one('product.product',readonly=True)
    # uom = fields.Many2one('uom.uom')
    product_uom_inherite = fields.Many2one('uom.uom', string='Product Unit of Measure')
    vend_id = fields.Many2one('res.partner')
    generate_date = fields.Datetime(string='Date', default=lambda self: fields.datetime.now())
    go_po = fields.Boolean('Send To P.O')
    stock = fields.Char(string='Stock',readonly=True)


    bridge_rel = fields.Many2one('purchase.planning')

class AddPonsPurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    bonus_qty = fields.Integer()
    initial_qty = fields.Integer()
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True,
                               compute='sum_bons')
    @api.onchange('initial_qty')
    def set_initial(self):
        for rec in self:
            rec.initial_qty = 1

    @api.depends('bonus_qty', 'initial_qty')
    def sum_bons(self):
        for i in self:
            i.product_qty = i.bonus_qty + i.initial_qty

class UunitOfMeasureNotRequired(models.Model):
    _inherit = 'purchase.order'

    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    pharmacy_number = fields.Char(string='Pharmacy Number')






########## Last Version

# @api.multi
# def create_records(self):
#     lines = []
#     for rec in self:
#         rec.relation_fiel.unlink()
#         for stock in rec.internal_stock:
#             stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
#             category_obj = stock.env['product.product'].search([['categ_id', '=', rec.product_category.id]])
#             for obj in stock_obj:
#                 sold = stock.env['sale.order.line'].search([('product_id', '=', obj.product_id.id)])
#                 pos_sold = stock.env['pos.order.line'].search([('product_id', '=', obj.product_id.id)])
#                 pos_qty = 0
#                 for line in pos_sold:
#                     pos_qty = pos_qty + line.qty
#                 for x in sold:
#                     if x.qty_delivered:
#                         dates = x.order_id.confirmation_date
#                 if (rec.date_to >= dates >= rec.date_from) and (category_obj):
#                     qty = 0
#                     for line in sold:
#                         qty = qty + line.qty_delivered
#                     for line in obj.product_id.seller_ids:
#                         vend = line.name
#                     po_obj = stock.env['purchase.order'].search([('product_id', '=', obj.product_id.id)],
#                                                                 limit=1)
#                     last_po = po_obj.name
#                     po_date = stock.env['purchase.order'].search([('product_id', '=', obj.product_id.id)],
#                                                                  limit=1)
#                     po_date_obj = po_date.date_order
#                     po_received = stock.env['purchase.order.line'].search(
#                         [('product_id', '=', obj.product_id.id)], limit=1)
#                     po_qty_received = po_received.qty_received
#                     po_last_price = po_received.price_unit
#                     concat_stock = str(obj.location_id.location_id.name) + '/' + obj.location_id.name
#                     lines.append({
#                         'stock' : concat_stock,
#                         'prod_id': obj.product_id.id,
#                         'product_uom_inherite': po_received.product_uom,
#                         'current_balance': obj.quantity,
#                         'last_po_quantity': po_qty_received,
#                         'last_price_po': po_last_price,
#                         'vend_id': vend,
#                         'pos_salable_quantity': pos_qty,
#                         'salable_quantity': qty,
#                         'quantity': (qty + pos_qty) - obj.quantity,
#                         'demand_qty': (qty + pos_qty) - obj.quantity,
#                         'last_po_num': last_po,
#                         'last_po_date': po_date_obj
#                     })
#         rec.relation_fiel = lines
#     return lines

