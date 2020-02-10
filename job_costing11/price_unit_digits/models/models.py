# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PriceUnitDigits(models.Model):
    _inherit = 'purchase.order.line'

    price_unit = fields.Float(string='Unit Price', required=True, digits=(16, 3))


class PriceUnitDigitsInvoice(models.Model):
    _inherit = 'account.invoice.line'

    price_unit = fields.Float(string='Unit Price', required=True, digits=(16, 3))
