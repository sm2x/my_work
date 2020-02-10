

from odoo import fields,models,api

class ProductBalanceStocks(models.Model):
    _name = 'product.balance.stocks'
    # _rec_name = "prod_id"

    location = fields.Many2many('stock.location',string='Location', default=lambda self: self._default_get())
    prod_id = fields.Many2many('product.product', string='Product')
    product_category = fields.Many2one('product.category', string='Product Category')
    product_balance_lines = fields.One2many('product.balance.stocks.line','items_line')

    @api.model
    def _default_get(self):
        return self.env['stock.location'].search([('location_id', '=', self.id) and ('usage', '=', 'internal')]).ids

    @api.multi
    def get_products(self):
        lines = []
        for rec in self:
            rec.product_balance_lines.unlink()
            for stock in rec.location:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                prod_l = []
                for i in rec.prod_id:
                    prod_l.append(i.name)
                for obj in stock_obj:
                    if (obj.product_id.categ_id.name == rec.product_category.name) \
                            or (obj.product_id.name in prod_l) :
                        lines.append({
                            'product': obj.product_id.id,
                            'location': obj.location_id.name,
                            'qty': obj.quantity,
                        })
            res = []
            [res.append(x) for x in lines if x not in res]
            rec.product_balance_lines = res
            return res


class ProductBalanceStocksLine(models.Model):
    _name = 'product.balance.stocks.line'

    items_line = fields.Many2one('product.balance.stocks')

    location = fields.Char(string='Location')
    qty = fields.Integer(string='Qty')
    product = fields.Many2one('product.product', string='Product')
    refrence = fields.Char(string='Reference', related='product.default_code')
    sale_price = fields.Float(string='Sale Price', related='product.list_price')



