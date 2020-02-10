
from odoo import models, fields, api
from datetime import datetime

class TransferReport(models.Model):
    _name = 'internal.transfer'
    _rec_name = 'from_location'

    date_from = fields.Datetime(string='Date From',required=True)
    date_to = fields.Datetime(string='Date To',required=True)
    from_location = fields.Many2one('stock.location',string='From Location')
    to_location = fields.Many2many('stock.location', string='To Location', default=lambda self: self._default_get())
    prod_id = fields.Many2one('product.product', string='Product')

    internal_line = fields.One2many('internal.transfer.line','internal_line')

    @api.model
    def _default_get(self):
        return self.env['stock.location'].search([('location_id', '=', self.id) and ('usage', '=', 'internal')]).ids

    @api.multi
    def create_transfer_line(self):
        lines = []
        for rec in self:
            rec.internal_line.unlink()
            loc_list = []
            for i in rec.from_location:
                loc_list.append(i.name)
            for stock in rec.to_location:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                for obj in stock_obj:
                    lines_picking = stock.env['stock.picking'].search([('product_id', '=', obj.product_id.id)])
                    for line in lines_picking:
                        location_list = []
                        trans_qty = 0
                        for q in line.move_ids_without_package:
                            trans_qty = q.quantity_done
                        for i in rec.to_location:
                            location_list.append(i.name)
                        # if (rec.from_location.id == line.location_id.id) and (line.location_dest_id.id in loc_l):
                        # (rec.to_location.id == line.location_dest_id.id)
                        if (rec.from_location.id == line.location_id.id) and (any(x == line.location_dest_id.name for x in location_list))  :
                            concat_stock_from = rec.from_location.name # str(obj.location_id.location_id.name) + '/' +
                            concat_stock_to =  line.location_dest_id.name # str(obj.location_id.location_id.name) + '/' +

                            if rec.prod_id:
                                prod_l = []
                                for i in rec.prod_id:
                                    prod_l.append(i.name)
                                if (obj.product_id.name in prod_l):
                                    lines.append({
                                        'product': obj.product_id.id,
                                        'refrence': obj.product_id.default_code,
                                        'from_loc': concat_stock_from,
                                        'to_loc': concat_stock_to,
                                        'transfer_qty' : trans_qty,
                                        # 'product_no' : line.move_ids_without_package,
                                        'date_sch': line.scheduled_date,
                                        'status': line.state
                                    })
                            elif (rec.date_to >= line.scheduled_date >= rec.date_from):
                                lines.append({
                                            'product': obj.product_id.id,
                                            'refrence': obj.product_id.default_code,
                                            'from_loc': concat_stock_from,
                                            'to_loc': concat_stock_to,
                                            'transfer_qty': trans_qty,
                                            # 'product_no' : line.move_ids_without_package,
                                            'date_sch': line.scheduled_date,
                                            'status': line.state
                                        })
            # To remove Dublicate
            res = []
            [res.append(x) for x in lines if x not in res]
            rec.internal_line = res

        return lines




class StockCardLine(models.Model):
    _name = 'internal.transfer.line'

    internal_line = fields.Many2one('internal.transfer')

    product = fields.Many2one('product.product')
    refrence = fields.Char(string='Reference',related='product.default_code')
    from_loc = fields.Char(string='From')
    to_loc = fields.Char(string='To')
    date_sch = fields.Datetime(string='Date')
    move_ids = fields.Many2one('stock.move')
    transfer_qty = fields.Integer(string='Transfer Qty')

    # @api.onchange('to_loc')
    # def defualt(self):
    #     self.to_loc = 'nona'






