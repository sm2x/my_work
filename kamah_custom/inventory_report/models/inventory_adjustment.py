
from odoo import fields,models,api

class InventoryAdjustment(models.Model):
    _name = 'inventory.adjustment'
    # _rec_name = "location"

    location = fields.Many2many('stock.location', string='Location', default = lambda self: self._default_get())
    prod_id = fields.Many2many('product.product', string='Product')
    date_from = fields.Datetime(string='Date From', required=True)
    date_to = fields.Datetime(string='Date To', required=True)
    adjustment_lines = fields.One2many('inventory.adjustment.line','adjust_line')

    @ api.model
    def _default_get(self):
        return self.env['stock.location'].search([('location_id', '=', self.id) and ('usage', '=', 'internal')]).ids

    @api.multi
    def create_adjustment_line(self):
        lines = []
        for rec in self:
            rec.adjustment_lines.unlink()
            for stock in rec.location:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                for obj in stock_obj:
                    lines_adj = stock.env['stock.inventory.line'].search([('product_id', '=', obj.product_id.id)])
                    for i in lines_adj:
                        theoretical_q = i.theoretical_qty
                        real_q = i.product_qty
                        po_d = i.po_date
                        vend = ''
                        for line in obj.product_id.seller_ids:
                            vend = line.name
                        if  stock.id == i.location_id.id:
                            if rec.prod_id:
                                prod_l = []
                                for i in rec.prod_id:
                                    prod_l.append(i.name)
                                if (obj.product_id.name in prod_l):
                                    lines.append({
                                        'product': obj.product_id.id,
                                        'refrence': obj.product_id.default_code,
                                        'cost': obj.product_id.standard_price,
                                        'vend_id': vend,
                                        'theoritcal_Qty':theoretical_q,
                                        'real_qty' : real_q,
                                        'po_date' : po_d,
                                        'date': lines_adj.inventory_id.date
                                    })
                            elif (rec.date_to >= lines_adj.inventory_id.date >= rec.date_from):
                                lines.append({
                                'product': obj.product_id.id,
                                'refrence': obj.product_id.default_code,
                                'cost': obj.product_id.standard_price,
                                'vend_id': vend,
                                'theoritcal_Qty': theoretical_q,
                                'real_qty': real_q,
                                'po_date': po_d,
                                'date': lines_adj.inventory_id.date
                            })
            rec.adjustment_lines = lines
        return lines


class InventoryAdjustmentLine(models.Model):
    _name = 'inventory.adjustment.line'

    product = fields.Many2one('product.product', string='Product')
    refrence = fields.Char(string='Reference', related='product.default_code')
    # cost = fields.Float(related='product.standard_price')
    vend_id = fields.Many2one('res.partner', string='Vendor')
    theoritcal_Qty = fields.Integer(string='Theoritcal Qty')
    real_qty = fields.Integer(string='Real Quantity')
    unit_cost = fields.Float(string='Unit Cost', related='product.standard_price')
    po_date = fields.Datetime(string='Po Date')
    date = fields.Datetime(string='Date')
    adjust_line = fields.Many2one('inventory.adjustment')


