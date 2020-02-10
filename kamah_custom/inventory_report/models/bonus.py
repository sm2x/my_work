
from odoo import api, fields, models, _

class Bonus(models.Model):
    _name = 'bonus'
    # _rec_name = "location"

    location = fields.Many2many('stock.location',string='Location' ,default=lambda self: self._default_get())
    prod_id = fields.Many2many('product.product', string='Product')
    date_from = fields.Datetime(string='Date From', required=True)
    date_to = fields.Datetime(string='Date To', required=True)
    bonus_lines = fields.One2many('bonus.line','bonus_line')

    @api.model
    def _default_get(self):
        return self.env['stock.location'].search([('location_id', '=', self.id) and ('usage', '=', 'internal')]).ids

    @api.multi
    def print_report(self):
        return self.env.ref('inventory_report.bonus_report').report_action(self)

    @api.multi
    def create_bonus_lines(self):
        self.ensure_one()
        lines = []
        for rec in self:
            rec.bonus_lines.unlink()
            for stock in rec.location:
                stock_obj = stock.env['stock.quant'].search([['location_id', '=', stock.id]])
                for obj in stock_obj:
                    po_obj = rec.env['purchase.order'].search([('product_id', '=', obj.product_id.id)])
                    picking = stock.env['stock.picking'].search([('product_id', '=', obj.product_id.id)])
                    bon_q = 0
                    init_q = 0
                    prod_q = 0
                    receiv_q = 0
                    inovic_q = 0
                    for i in po_obj:
                        vend = i.partner_id.id
                        po_r = i.name
                        po_d = i.date_order
                        po_sch = i.date_planned
                        for x in i.order_line:
                            bon_q = x.bonus_qty
                            init_q = x.initial_qty
                            prod_q = x.product_qty
                            receiv_q = x.qty_received
                            inovic_q = x.qty_invoiced
                        for i in picking:
                            if i.picking_type_id.name == 'Receipts' and (i.location_dest_id.id == stock.id):
                                if rec.prod_id:
                                    prod_l = []
                                    for i in rec.prod_id:
                                        prod_l.append(i.name)
                                    if (obj.product_id.name  in prod_l):
                                        lines.append({
                                            'product': obj.product_id.id,
                                            'refrence': obj.product_id.default_code,
                                            'vend_id': vend,
                                            'bonus_qty': bon_q,
                                            'intial_qty': init_q,
                                            'product_qty': prod_q,
                                            'recieved_qty': receiv_q,
                                            'billed_qty': inovic_q,
                                            'po_ref': po_r,
                                            'po_date': po_d
                                        })
                                elif (rec.date_to >= po_d >= rec.date_from) :
                                    lines.append({
                                            'product': obj.product_id.id,
                                            'refrence': obj.product_id.default_code,
                                            'vend_id': vend,
                                            'bonus_qty': bon_q,
                                            'intial_qty': init_q,
                                            'product_qty': prod_q,
                                            'recieved_qty': receiv_q,
                                            'billed_qty': inovic_q,
                                            'po_ref': po_r,
                                            'po_date': po_d
                                        })
            # To remove Dublicate
            res = []
            [res.append(x) for x in lines if x not in res]
            rec.bonus_lines = res
        return lines


class BonusLine(models.Model):
    _name = 'bonus.line'

    product = fields.Many2one('product.product', string='Product')
    refrence = fields.Char(string='Reference', related='product.default_code')
    vend_id = fields.Many2one('res.partner', string='Vendor')
    po_ref = fields.Char(string='Po Reference')
    po_date = fields.Datetime(string='Po Date')
    bonus_qty = fields.Integer(string='Bonus Qty')
    intial_qty = fields.Integer(string='Initial Qty')
    product_qty = fields.Integer(string='Total Qty')
    recieved_qty = fields.Integer(string='Recieved Qty')
    billed_qty = fields.Integer(string='Billed Qty')
    cost = fields.Float(related='product.seller_ids.price')
    bonus_Value = fields.Float(string='Bonus Value',compute='get_value')
    bonus_line = fields.Many2one('bonus')

    @api.depends('cost','bonus_qty')
    def get_value(self):
        for rec in self:
            rec.bonus_Value = rec.cost * rec.bonus_qty




