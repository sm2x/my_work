
from odoo import models, fields, api


class ScrapProduct(models.Model):
    _name = 'scrap.product'
    # _rec_name = "location"

    location = fields.Many2many('stock.location', required=True, string='Location',default=lambda self: self._default_get())
    prod_id = fields.Many2many('product.product', string='Product')
    date_from = fields.Datetime(string='Date From', required=True)
    date_to = fields.Datetime(string='Date To', required=True)
    scrap_lines = fields.One2many('scrap.product.line','scrap_product',string='Scrap Products')

    @api.model
    def _default_get(self):
        return self.env['stock.location'].search([('location_id', '=', self.id) and ('usage', '=', 'internal') ]).ids

    @api.multi
    def create_scrap_product_line(self):
        lines = []
        for rec in self:
            rec.scrap_lines.unlink()
            loc_l = []
            for i in rec.location:
                loc_l.append(i.name)
            prod_l = []
            for i in rec.prod_id:
                prod_l.append(i.name)
            for stock in rec.location:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                for obj in stock_obj:
                    po_obj = rec.env['purchase.order.line'].search([('product_id', '=', obj.product_id.id)])
                    purchase_cost = 0
                    for i in po_obj:
                        purchase_cost = i.price_unit
                    prod_scrap = stock.env['stock.scrap'].search([('product_id', '=', obj.product_id.id)])
                    for lin in prod_scrap:
                        scrap_p = lin.scrap_qty
                        scrap_date = lin.create_date
                        vend = ''
                        for line in obj.product_id.seller_ids:
                            vend = line.name
                        if (lin.location_id.name in loc_l):
                            if rec.prod_id:
                                if (obj.product_id.name in prod_l) :
                                    lines.append({
                                        'product': obj.product_id.id,
                                        'refrence': obj.product_id.default_code,
                                        'cost' : purchase_cost,
                                        'vend_id': vend,
                                        'total_qty': scrap_p,
                                        'tot_cost': scrap_p * obj.product_id.standard_price
                                    })
                            elif  (rec.date_to >= scrap_date >= rec.date_from):
                                lines.append({
                                    'product': obj.product_id.id,
                                    'refrence': obj.product_id.default_code,
                                    'cost': purchase_cost,
                                    'vend_id': vend,
                                    'total_qty': scrap_p,
                                    'tot_cost': scrap_p * obj.product_id.standard_price
                                })
            # To remove Dublicate
            res = []
            [res.append(x) for x in lines if x not in res]
            rec.scrap_lines = res
        return lines


class ScrapProductLine(models.Model):
    _name = 'scrap.product.line'

    product = fields.Many2one('product.product', string='Product')
    refrence = fields.Char(string='Reference', related='product.default_code')
    cost = fields.Float(string='Cost')
    vend_id = fields.Many2one('res.partner', string='Vendor')
    total_qty = fields.Integer(string='Total Qty')
    avg_cost = fields.Float(string='Average Cost', compute='get_average')
    tot_cost = fields.Float(string='Total Cost')
    scrap_product = fields.Many2one('scrap.product')


    @api.depends('cost','total_qty')
    def get_average(self):
        for rec in self:
            rec.avg_cost = rec.cost / rec.total_qty
