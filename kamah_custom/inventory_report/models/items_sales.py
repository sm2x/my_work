
from odoo import fields,models,api

class ItemsSales(models.Model):
    _name = 'items.sales'
    _rec_name = "product_category"

    location = fields.Many2many('stock.location', readonly=False, string='Location', default=lambda self: self._default_get())
    prod_id = fields.Many2many('product.product', string='Product')
    date_from = fields.Datetime(string='Date From', required=True)
    date_to = fields.Datetime(string='Date To', required=True)
    product_category = fields.Many2one('product.category', string='Product Category')
    items_sales_lines = fields.One2many('items.sales.line','items_line')

    @api.model
    def _default_get(self):
        return self.env['stock.location'].search([('location_id', '=', self.id) and ('usage', '=', 'internal')]).ids

    @api.multi
    def create_items_sale_lines(self):
        lines = []
        for rec in self:
            rec.items_sales_lines.unlink()
            for stock in rec.location:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                for obj in stock_obj:
                    products_lines = stock.env['sale.order.line'].search([('product_id', '=', obj.product_id.id)],
                                                                         limit=1)
                    picking = stock.env['stock.picking'].search([('product_id', '=', obj.product_id.id)])
                    for i in products_lines:
                        date_conf = i.order_id.confirmation_date
                        for x in picking:
                            if x.picking_type_id.name == 'Delivery Orders' and (x.location_id.id == stock.id):
                                if rec.prod_id:
                                    prod_l = []
                                    for i in rec.prod_id:
                                        prod_l.append(i.name)
                                    if (obj.product_id.categ_id.name == rec.product_category.name) \
                                            or (obj.product_id.name in prod_l):
                                        lines.append({
                                            'product': obj.product_id.id,
                                            'sales_pr': products_lines.price_unit,
                                            'sold_qty': products_lines.qty_delivered,
                                            'onhand_qty': obj.quantity,
                                            'product_uom': products_lines.product_uom,
                                            'product_category': obj.product_id.categ_id
                                        })
                                elif (rec.date_to >= date_conf >= rec.date_from):
                                    lines.append({
                                        'product': obj.product_id.id,
                                        'sales_pr': products_lines.price_unit,
                                        'sold_qty': products_lines.qty_delivered,
                                        'onhand_qty': obj.quantity,
                                        'product_uom': products_lines.product_uom,
                                        'product_category': obj.product_id.categ_id
                                    })

            rec.items_sales_lines = lines
        return lines


class ItemsSalesLine(models.Model):
    _name = 'items.sales.line'

    product = fields.Many2one('product.product', string='Product')
    refrence = fields.Char(string='Reference', related='product.default_code')
    cost = fields.Float(related='product.standard_price')
    sales_pr = fields.Float(string='Sales Price')
    sold_qty = fields.Integer(string='Sold Qty')
    onhand_qty = fields.Integer(string='On Hand Qty')
    tot_sales_pr = fields.Float(string='Total Sold Price', compute='get_total_sales')
    tot_cost = fields.Float(string='Total Cost', compute='get_total_cost')
    product_uom = fields.Many2one('uom.uom', string='Product UOM')
    product_category = fields.Many2one('product.category', string='Product Category')
    items_line = fields.Many2one('items.sales')

    @api.depends('sales_pr','sold_qty')
    def get_total_sales(self):
        for rec in self:
            rec.tot_sales_pr = rec.sales_pr * rec.sold_qty

    @api.depends('cost','sold_qty')
    def get_total_cost(self):
        for rec in self:
            rec.tot_cost = rec.cost * rec.sold_qty




