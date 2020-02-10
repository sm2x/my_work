
from odoo import models, fields, api
from datetime import datetime


class StockCard(models.Model):
    _name = 'stock.card'
    _rec_name = "stock"

    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    warehouse = fields.Many2one('stock.warehouse', string='Warehouse')
    stock = fields.Many2one('stock.location')
    product_category = fields.Many2one('product.category', string='Product Category')
    card_line = fields.One2many('stock.card.line','stock_card')

    @api.multi
    def create_record(self):
        lines = []
        for rec in self:
            rec.card_line.unlink()
            for stock in rec.stock:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                for obj in stock_obj:
                    paid = stock.env['purchase.order.line'].search([('product_id', '=', obj.product_id.id)])
                    qty_paid = 0
                    for line in paid:
                        qty_paid = qty_paid + line.product_qty
                    picking = stock.env['stock.picking'].search([('product_id', '=', obj.product_id.id)])
                    done = stock.env['stock.move'].search([('product_id', '=', obj.product_id.id)])
                    po_received = stock.env['purchase.order.line'].search([('product_id', '=', obj.product_id.id)], limit=1)
                    prod_scrap = stock.env['stock.scrap'].search([('product_id', '=', obj.product_id.id)])


                    dates = datetime.now()
                    for x in picking:
                        dates = x.date_done
                    if  (rec.end_date >= dates >= rec.start_date) or\
                            (obj.product_id.categ_id.name == rec.product_category.name) :
                        qty_delivery = 0
                        for line in picking:
                            if line.picking_type_id.name == 'Delivery Orders' and (line.location_id.id == rec.stock.id):
                                for i in line.move_ids_without_package:
                                    qty_delivery = i.quantity_done
                        qty_receipt = 0
                        internal_qty_source = 0
                        internal_qty_dest = 0
                        qty_scrp = 0
                        for lin in prod_scrap:     
                            if lin.location_id.id == rec.stock.id:
                                qty_scrp = qty_scrp + lin.scrap_qty
                        for line in done:
                            if (line.picking_type_id.name == 'Receipts') and (line.location_dest_id.id == rec.stock.id):
                                qty_receipt += line.quantity_done
                            if line.picking_type_id.name == 'Internal Transfers':
                                if line.location_id.id == stock.id:
                                    internal_qty_dest = line.quantity_done
                                if line.location_dest_id.id == stock.id:
                                    internal_qty_source = line.quantity_done
                        lines.append({
                        'product': obj.product_id.id,
                        'refrence' : obj.product_id.default_code,
                        'product_uom' : po_received.product_uom,
                        'initial_stock': obj.quantity,
                        'inn' : qty_receipt + internal_qty_source,
                        'out': internal_qty_dest + qty_delivery + qty_scrp,
                        })
            rec.card_line = lines
        return lines


class StockCardLine(models.Model):
    _name = 'stock.card.line'

    stock_card = fields.Many2one('stock.card')
    product = fields.Many2one('product.product')
    refrence = fields.Char(string='Reference') #,related='product.default_code')
    product_uom = fields.Many2one('uom.uom',string='Product UOM')
    initial_stock = fields.Float(string='Initial Stock')
    inn = fields.Float(string='In',domain=['|',('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)])
    out = fields.Float(string='Out')
    balance = fields.Float(string='Balance', compute='get_balance')
    final_Stock = fields.Float(string='Final Stock', compute='get_final')


    @api.depends('inn','out')
    def get_balance(self):
        for rec in self:
            rec.balance = rec.inn - rec.out

    @api.depends('inn', 'out')
    def get_final(self):
        for rec in self:
            rec.final_Stock = rec.inn - rec.out
