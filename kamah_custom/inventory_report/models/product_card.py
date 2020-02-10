from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductCard(models.Model):
    _name = "product.card"

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('product.card.seq')
        })
        return super(ProductCard, self).create(vals)

    name = fields.Char('name')

    product_id = fields.Many2one('product.product', string='Product')
    location_id = fields.Many2one('stock.location', string='Location')
    date_to = fields.Datetime('Date To')
    date_from = fields.Datetime('Date From')
    card_line_ids = fields.One2many('product.card.line', 'card_id', string='Card Lines')

    def get_lines(self):
        lines = []
        if self.card_line_ids:
            self.card_line_ids.unlink()

        if self.product_id and self.location_id:
            product_moves = self.env['stock.move.line'].search([('product_id', '=', self.product_id.id),
                                                                ('state', '=', 'done'),
                                                                # '&',
                                                                '|',
                                                                ('location_dest_id', '=', self.location_id.id), ('location_id', '=', self.location_id.id),
                                                                # '|',
                                                                # ('location_dest_id.location_id', '=', self.location_id.id), ('location_id.location_id', '=', self.location_id.id)
                                                                ])

            if product_moves:
                for move in product_moves:
                    print('move', move.reference)
                    # print('move', move.date)
                    # print('move', move.product_id.name)
                    # print('move', move.location_id.name)
                    # print('move', move.location_dest_id.name)

                    date = move.date
                    if self.date_to >= date >= self.date_from:
                        print(date)\
                        # or (move.location_id.location_id == self.location_id)
                        if move.location_id == self.location_id:
                            print('inn')
                            lines.append({
                                'product_id': move.product_id.id,
                                'reference': move.reference,
                                'location_id': move.location_id.id,
                                'date': move.date,
                                'in_qty': 0.0,
                                'out_qty': move.qty_done,
                            })
                            # or (move.location_id.location_id == self.location_id):

                        if move.location_dest_id == self.location_id:
                            print('out')
                            lines.append({
                                'product_id': move.product_id.id,
                                'date': move.date,
                                'reference': move.reference,
                                'location_id': move.location_dest_id.id,
                                'in_qty': move.qty_done,
                                'out_qty': 0.0,
                            })
            else:
                print('No moves')
                raise ValidationError('There is no Moves for this Product in this Location')

        # print(lines)
        self.card_line_ids = lines
        # self.compute_line_num()
        self.compute_balance()

    # def compute_line_num(self):
    #     init_no = 1
    #     for line in self.card_line_ids:
    #         print(line.line_num)
    #         line.line_num = init_no
    #         init_no = init_no+1

    def compute_balance(self):
        for rec in self:
            product_moves = self.env['stock.move.line'].search([('product_id', '=', rec.product_id.id),
                                                                ('state', '=', 'done')])
            print(product_moves[0].reference)
            print(product_moves[0].qty_done)
            last_b = product_moves[0].qty_done
            for line in rec.card_line_ids:
                # if line.line_num == 1:
                line.init_balance = last_b
                line.balance = line.init_balance+(line.in_qty-line.out_qty)
                last_b = line.balance
                # else:
                #     line.balance = line.init_balance+(line.in_qty-line.out_qty)


class ProductCardLine(models.Model):
    _name = 'product.card.line'

    card_id = fields.Many2one('product.card')
    # line_num = fields.Integer('unm')
    product_id = fields.Many2one('product.product', string='Product')
    location_id = fields.Many2one('stock.location', string='Location')
    reference = fields.Char(string='Reference')
    date = fields.Datetime('Date To')
    init_balance = fields.Float('Init Balance')
    in_qty = fields.Float('IN')
    out_qty = fields.Float('OUT')
    balance = fields.Float('Balance')
