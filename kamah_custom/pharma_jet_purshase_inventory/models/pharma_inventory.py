
from odoo import models, fields, api, _
from datetime import datetime


class Location_field(models.Model):
    _inherit = 'stock.location'
    # _name = 'location.field'

    validation_transfer_internal = fields.Many2many('res.partner',string='Validation Transfer Internal')


class TransferPlanning(models.Model):
    _name = 'transfer.planning'

    name = fields.Char(string='Code', index=True, readonly=True)
    internal_stock = fields.Many2many('stock.location')
    date_from = fields.Datetime(string='Date From', required=True , default= datetime.today())
    date_to = fields.Datetime(string='Date To', required=True, default= datetime.today())
    sales_period = fields.Integer(string='Sales Period Per Day', compute='get_duration_per_day')
    sales_period_rate = fields.Integer(string='Sales Period Rate',readonly=False, default=1)
    days_rate_supply = fields.Integer(string='Days Rate To Supply',compute='get_supply')
    location_ids = fields.Many2one('stock.location', string="Source Location" ,required=True,
                                   default=lambda self: self.env.user
                                   )
    location_dest_ids = fields.Many2one('stock.location', string="Destination Location",required=True,
                                        default=lambda self: self.env.user)
    picking_type_ids = fields.Many2one('stock.picking.type', string='Operation Type',required=True,
                                       default=lambda self: self.env.user
                                       )
    transfer_line = fields.One2many('transfer.planning.line','trans_plan')



    @api.model
    def create(self, vals):
        # serial_for_transefer_planning => this act id for view
        # name => this act field name
        # TransferPlanning => module name

        sequence = self.env['ir.sequence'].next_by_code('serial_for_transefer_planning')
        vals['name'] = sequence
        result = super(TransferPlanning, self).create(vals)
        # print(result)
        return result

    @api.depends('date_from', 'date_to')
    def get_duration_per_day(self):
        if self.date_to:
            d1 = self.date_from
            d2 = self.date_to
            self.sales_period = (d2 - d1).days

    @api.depends('sales_period_rate')
    def get_supply(self):
        self.days_rate_supply = (self.sales_period / self.sales_period_rate)

    @api.multi
    def create_internal_transfer(self):
        trans_vals = {}
        t_obj = self.env['stock.picking']
        line_ids = []
        for rec in self:
            for i in rec.transfer_line:
                for line in i:
                    if line.go_it == True:
                        line_ids.append((0, 0, {
                            'product_id': line.product.id,
                            'name': line.product.id,
                            'product_uom': line.product_uom_inherite.id,
                            'product_uom_qty': line.real_demand_qty
                        }))
                        vals = {
                            'location_id': self.location_ids.id,
                            'location_dest_id': self.location_dest_ids.id,
                            'picking_type_id': self.picking_type_ids.id,
                            'move_ids_without_package' : line_ids
                        }
                        trans_vals = vals
            print(trans_vals)
            t_obj.create(trans_vals)




    @api.multi
    def create_transfer_line(self):
        self.transfer_line.unlink()
        lines = []
        for rec in self:
            for stock in rec.internal_stock:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                for obj in stock_obj:
                    sold = stock.env['sale.order.line'].search([('product_id', '=', obj.product_id.id)])
                    pos_sold = stock.env['pos.order.line'].search([('product_id', '=', obj.product_id.id)])
                    po_received = stock.env['purchase.order.line'].search([('product_id', '=', obj.product_id.id)], limit=1)
                    pos_qty = 0
                    for line in pos_sold:
                        pos_qty = pos_qty + line.qty
                    for x in sold:
                        if x.qty_delivered:
                            dates = x.order_id.confirmation_date
                    if (rec.date_to >= dates >= rec.date_from):
                        qty = 0
                        for line in sold:
                            qty = qty + line.qty_delivered
                        lines.append({
                                    'product': obj.product_id.id,
                                    'product_uom_inherite': po_received.product_uom,
                                    'current_balance': obj.quantity,
                                    'pos_prod': pos_qty,
                                    'sale_prod': qty,
                                    'total_sold_qty': (qty + pos_qty),
                                    'days_rate_supply' : rec.sales_period_rate,
                                    'sold_qty_rate' : ((qty + pos_qty) / rec.sales_period_rate),
                                    'qty_demand' : (((qty + pos_qty) / rec.sales_period_rate) - obj.quantity) ,
                                    'real_demand_qty' : (((qty + pos_qty) / rec.sales_period_rate) - obj.quantity)
                                })

        rec.transfer_line = lines
        print(lines)
        return lines


class TransferPlanningLine(models.Model):
    _name = 'transfer.planning.line'

    trans_plan = fields.Many2one('transfer.planning')
    go_it = fields.Boolean(string='Go Internal Transfer')
    product = fields.Many2one('product.product',string='Product',readonly=True)
    total_sold_qty = fields.Integer('Total Sold Qty',readonly=True)
    days_rate_supply = fields.Integer(string='Days Rate To Supply',readonly=True)
    sold_qty_rate = fields.Integer(string='Sold Qty Based On Days Rate',readonly=True)
    current_balance = fields.Integer(string='Current Balance',readonly=True)
    qty_demand = fields.Integer(string='Qty To Demand',readonly=True)
    real_demand_qty = fields.Integer(string='Real Demand Qty')
    sale_prod = fields.Integer()
    pos_prod = fields.Integer()
    product_uom_inherite = fields.Many2one('uom.uom', string='Product Unit of Measure')

class OperationsType(models.Model):
    _inherit = 'stock.picking.type'

    internal_trans_approv = fields.Boolean(string='Internal Transfer Approval',default=False)
    rel_field = fields.Many2one('stock.move')

    @api.onchange('internal_trans_approv', 'rel_field.test', 'test')
    def onchange_true(self):
        for line in self:
                asd = self.env['stock.picking'].search([('picking_type_id', '=', line.name)])
                for record in asd:
                    record.write({
                        'test1': line.internal_trans_approv
                    })

class StockPicking(models.Model):
    _inherit = "stock.move"

    product = fields.Many2one('stock.quant')
    qty = fields.Float(string='Demand Qty', compute='get_qty')
    onhand = fields.Float(string='On Hand',related='product_id.qty_available')
    test = fields.Boolean(string='my test',related='picking_id.test1',readonly=False,copy=True,store=True)
    picking_code = fields.Selection(related='picking_id.picking_type_id.code', readonly=True,store=True)

    @api.depends('product_uom_qty')
    def get_qty(self):
        for rec in self:
            rec.qty = rec.product_uom_qty



class OperationsTypeTest(models.Model):
    _inherit = 'stock.picking'

    rel = fields.Many2one('stock.picking.type')
    relation_field = fields.Many2one('stock.picking.type')
    test1 = fields.Boolean(string='my test',copy=True,store=True)

class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    po = fields.Many2one('purchase.order')
    cost = fields.Float(string='Cost', related='product_id.standard_price')
    po_date = fields.Datetime(string='PO Date', compute='get_po_date')
    vend_id = fields.Many2one('res.partner',string='Vendor', compute='get_vendor')

    @api.multi
    def get_po_date(self):
        for rec in self:
            p_date = rec.env['purchase.order'].search([('product_id', '=', rec.product_id.id)],limit=1)
            rec.po_date = p_date.date_order


    @api.multi                                                                                           
    def get_vendor(self):
        for rec in self:
            partner = rec.env['purchase.order'].search([('product_id', '=', rec.product_id.id)],limit=1)
            rec.vend_id = partner.partner_id


class StockInventory(models.Model):
    _inherit = 'stock.inventory'



class StockMoveTree(models.Model):
    _inherit = 'stock.move.line'

    internals = fields.Selection(string='Internal', related='picking_id.picking_type_id.code', store=True)





