# -*- coding: utf-8 -*-

from odoo import models, fields


class OmmatPoultryProject(models.Model):
    _name = 'poultry.model'

    Date = fields.Date('Date')
    Lot_id = fields.Many2one('stock.production.lot', string='Lot')
    weight_ids = fields.One2many('weight.model', 'poultry_id', string='Weight')


class OmmatPoultryWeight(models.Model):
    _name = 'weight.model'

    weight = fields.Float(string='Weight')
    # weight_dis = fields.Float('Weight')
    poultry_id = fields.Many2one('poultry.model')
