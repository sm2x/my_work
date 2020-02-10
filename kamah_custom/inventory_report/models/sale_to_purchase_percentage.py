
from odoo import fields,models,api

class SaleToPuchasePercentage(models.Model):
    _name = 'sale.purchase.percentage'
    # _rec_name = "location"

    location = fields.Many2many('stock.location', string='Location', default=lambda self: self._default_get())
    prod_id = fields.Many2one('product.product', string='Product')
    date_from = fields.Datetime(string='Date From', required=True)
    date_to = fields.Datetime(string='Date To', required=True)
    percentage_lines = fields.One2many('sale.purchase.percentage.line','sales_line', string='Percentage Lines')

    @api.model
    def _default_get(self):
        return self.env['stock.location'].search([('location_id', '=', self.id) and ('usage', '=', 'internal')]).ids

    @api.multi
    def create_sale_percentage_line(self):
        lines = []
        for rec in self:
            rec.percentage_lines.unlink()
            loc_l = []
            for i in rec.location:
                loc_l.append(i.name)

            for stock in rec.location:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                for obj in stock_obj:
                    print('in date : ', obj.in_date , 'Quantity : ', obj.quantity)
                    start_qty = 0
                    if rec.date_to >= obj.in_date >= rec.date_from :
                        start_qty = obj.quantity
                    sold_line = stock.env['sale.order.line'].search([('product_id', '=', obj.product_id.id)])
                    stock_picking = stock.env['stock.picking'].search([('product_id', '=', obj.product_id.id)])
                    stock_move_line = stock.env['stock.move.line'].search([('product_id', '=', obj.product_id.id)])
                    qty_bal = 0
                    for s in stock_move_line:
                        if s.location_id.id == stock.id:
                            if rec.date_to >= s.date >= rec.date_from:
                                qty_bal += s.qty_done
                    prod_l = []
                    for i in rec.prod_id:
                        prod_l.append(i.name)
                    purchase_q = 0
                    sale_q = 0
                    for line in stock_picking:
                        if line.picking_type_id.name == 'Delivery Orders' and (stock.id == line.location_id.id) :
                            # if rec.date_to >= line.date_done >= rec.date_from:
                                for i in line.move_ids_without_package:
                                    sale_q += i.quantity_done
                    for line in stock_picking:
                        if line.picking_type_id.name == 'Receipts' and (stock.id == line.location_dest_id.id)  :
                            # if rec.date_to >= line.date_done  >= rec.date_from :
                                for i in line.move_ids_without_package:
                                    purchase_q += i.quantity_done
                    for x in sold_line:
                        dates = x.order_id.confirmation_date

                        if rec.prod_id:
                            if (obj.product_id.name in prod_l):
                                lines.append({
                                    'product': obj.product_id.id,
                                    'refrence': obj.product_id.default_code,
                                    'starting_balance': start_qty,
                                    'purchase_qty': purchase_q,
                                    'sales_qty': sale_q,
                                    # 'ending_balance': start_qty + purchase_q,
                                    'sales_ending_percentage': sale_q / (start_qty + purchase_q)
                                })
                        elif (rec.date_to >= obj.in_date >= rec.date_from):
                            lines.append({
                                'product': obj.product_id.id,
                                'refrence': obj.product_id.default_code,
                                'starting_balance': start_qty,
                                'purchase_qty': purchase_q,
                                'sales_qty': sale_q,
                                # 'ending_balance': start_qty + purchase_q,
                                'sales_ending_percentage': sale_q / (start_qty + purchase_q)
                            })
            rec.percentage_lines = lines
        return lines

class SaleToPuchasePercentageLine(models.Model):
    _name = 'sale.purchase.percentage.line'

    product = fields.Many2one('product.product', string='Product')
    refrence = fields.Char(string='Reference', related='product.default_code')
    starting_balance = fields.Integer(string='Starting Balance')
    purchase_qty = fields.Integer(string='Purchase')
    ending_balance = fields.Integer(string='Ending Balance')
    sales_qty = fields.Integer(string='Sales')
    sales_ending_percentage = fields.Float(string='Sales To Ending Balance Percentage %')
    sales_line = fields.Many2one('sale.purchase.percentage')
