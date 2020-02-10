
from odoo import models, fields, api
from datetime import datetime


class TotalInventory(models.Model):
    _name = 'total.inventory'
    # _rec_name = 'product_category'

    location = fields.Many2many('stock.location', readonly=False, string='Location', default=lambda self: self._default_get())
    product_category = fields.Many2many('product.category', string='Product Category')
    prod_id = fields.Many2many('product.product', string='Product') #,domain="[('categ_id', '=', product_category)]")
    vend_id = fields.Many2one('res.partner', string='Vendor') #, domain="[('categ_id', '=', product_category)]")
    total_inventory_line = fields.One2many('total.inventory.line','total_inventory',string='Report Data')

    @api.model
    def _default_get(self):
        return self.env['stock.location'].search([('location_id', '=', self.id) and ('usage', '=', 'internal')]).ids

    @api.multi
    def create_total_inventory_line(self):
        lines = []
        for rec in self:
            rec.ensure_one()
            rec.total_inventory_line.unlink()
            for stock in rec.location:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                prod_l = []
                for i in rec.prod_id:
                    prod_l.append(i.name)
                for obj in stock_obj:
                    for ven in obj.product_id.seller_ids:
                        vend = ven.name
                        if (obj.product_id.categ_id.name == rec.product_category.name) \
                                or (obj.product_id.name in prod_l) \
                                or (vend == rec.vend_id):
                            lines.append({
                                'product': obj.product_id.id,
                                'refrence': obj.product_id.default_code,
                                'product_uom': obj.product_id.uom_id,
                                'qty': obj.quantity,
                                'cost': obj.product_id.standard_price,
                                'sale_pric': obj.product_id.list_price,
                                'total_cost': (obj.quantity) * (obj.product_id.standard_price),
                                'total_price': (obj.quantity) * (obj.product_id.list_price)
                            })
                res = []
                [res.append(x) for x in lines if x not in res]
                rec.total_inventory_line = res
                return res




class TotalInventoryLine(models.Model):
    _name = 'total.inventory.line'

    total_inventory = fields.Many2one('total.inventory')
    product = fields.Many2one('product.product',string='Product')

    refrence = fields.Char(string='Reference', related='product.default_code')
    product_uom = fields.Many2one('uom.uom', string='Product UOM')
    qty = fields.Integer(string='Qty ', readonly=True)
    cost = fields.Float(string='Cost')
    sale_pric = fields.Float(string='Sale Price')
    total_cost = fields.Float(string='Total Cost')
    total_price = fields.Float(string='Total Sale Price')



