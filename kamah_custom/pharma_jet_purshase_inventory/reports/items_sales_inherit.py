
from odoo import fields,models,api
import datetime

class ItemsSalesInherit(models.Model):
    _inherit = 'items.sales'

    # This function edit brand to it

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
                                            'brand' : obj.product_id.brand.id,
                                            'sales_pr': products_lines.price_unit,
                                            'sold_qty': products_lines.qty_delivered,
                                            'onhand_qty': obj.quantity,
                                            'product_uom': products_lines.product_uom,
                                            'product_category': obj.product_id.categ_id
                                        })
                                elif (rec.date_to >= date_conf >= rec.date_from):
                                    lines.append({
                                'product': obj.product_id.id,
                                'brand': obj.product_id.brand.id,
                                'sales_pr': products_lines.price_unit,
                                'sold_qty': products_lines.qty_delivered,
                                'onhand_qty': obj.quantity,
                                'product_uom': products_lines.product_uom,
                                'product_category': obj.product_id.categ_id
                            })

            rec.items_sales_lines = lines
        return lines


class ItemsSalesLineInherit(models.Model):
    _inherit = 'items.sales.line'

    brand = fields.Many2one('brand')


