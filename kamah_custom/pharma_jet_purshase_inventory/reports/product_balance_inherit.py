
from odoo import fields,models,api

class ProductBalanceInherit(models.Model):
    _inherit = 'product.balance.stocks'

    brand = fields.Many2many('brand', string='Brand')

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
                brand_l = []
                for i in rec.brand:
                    brand_l.append(i.name)
                for obj in stock_obj:
                    if (obj.product_id.categ_id.name == rec.product_category.name) \
                            or (obj.product_id.brand.name in brand_l) \
                            or (obj.product_id.name in prod_l):
                        lines.append({
                            'product': obj.product_id.id,
                            'location': obj.location_id.name,
                            'qty': obj.quantity,
                            'bran': obj.product_id.brand.id
                        })
            res = []
            [res.append(x) for x in lines if x not in res]
            rec.product_balance_lines = res
            return res



class ProductBalanceInheritLine(models.Model):
    _inherit = 'product.balance.stocks.line'

    bran = fields.Many2one('brand')