
from odoo import models, fields, api
from datetime import datetime


class ItemCard(models.Model):
    _name = 'item.card'
    _rec_name = "stock"

    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    warehouse = fields.Many2one('stock.warehouse', string='Warehouse')
    stock = fields.Many2one('stock.location')
    product_category = fields.Many2one('product.category', string='Product Category')
    card_line = fields.One2many('item.card.line','stock_card')


class ItemCardLine(models.Model):
    _name = 'item.card.line'

    stock_card = fields.Many2one('item.card')
    dates = fields.Datetime('Date')
    product = fields.Many2one('product.product')
    refrence = fields.Char(string='Reference') #,related='product.default_code')
    from_loc = fields.Char(string='From')
    to_loc = fields.Char(string='To')
    qty = fields.Float('Quantity Done')
    product_uom = fields.Many2one('uom.uom',string='Product UOM')
    inn = fields.Float(string='In',domain=['|',('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)])
    out = fields.Float(string='Out')
    balance = fields.Float(string='Balance', compute='get_balance')
    stat = fields.Char('Status')


    @api.depends('inn','out')
    def get_balance(self):
        for rec in self:
            rec.balance = rec.inn - rec.out



