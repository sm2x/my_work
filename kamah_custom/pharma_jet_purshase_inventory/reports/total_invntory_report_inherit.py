
from odoo import fields,models,api

class TotalInventoryInheritReport(models.Model):
    _inherit = 'total.inventory'

    brand = fields.Many2many('brand',string='Brand')

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
                brand_l = []
                for i in rec.brand:
                    brand_l.append(i.name)

                for obj in stock_obj:
                    for ven in obj.product_id.seller_ids:
                        vend = ven.name

                        if (obj.product_id.categ_id.name == rec.product_category.name) \
                                or (obj.product_id.name in prod_l) \
                                or (obj.product_id.brand.name in brand_l) \
                                or ( vend == rec.vend_id) :
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