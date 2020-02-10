# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, UserError


class VendorModel(models.Model):
    _inherit = 'res.partner'

    vendor_type = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C')],
                                   string="Vendor Type")

    vendor_classification = fields.Selection([('new', 'New'), ('old', 'Old')],
                                             string="Vendor Classification")
    file_no = fields.Char('رقم الملف الضريبى')
    tax_data = fields.Text('مأمورية الضرائب')

#
# class ProductTemplateModel(models.Model):
#     _inherit = 'product.template'
#
#     alert_time = fields.Integer(string='Product Alert Time',
#                                 help='Number of days before an alert should be raised on the lot/serial number.',
#                                 default='60')
#
#
# class StockLocationModel(models.Model):
#     _inherit = 'stock.location'
#
#     capacity = fields.Float('السعه التخزينيه')
#     removal_strategy_id = fields.Many2one('product.removal', 'سياسة الصرف',
#                                           help="Defines the default method used for suggesting the exact location (shelf) where to take the products from, which lot etc. for this location. This method can be enforced at the product category level, and a fallback is made on the parent locations if none is set here.")
#
#
# class StockPickingModel(models.Model):
#     _inherit = 'stock.picking'
#
#     partner_id = fields.Many2one(
#         'res.partner', 'مورد/عميل',
#         states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
#
#
# class StockInventoryModel(models.Model):
#     _inherit = 'stock.inventory'
#
#     @api.model
#     def _default_location_id(self):
#         company_user = self.env.user.company_id
#         warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
#         if warehouse:
#             return warehouse.lot_stock_id.id
#         else:
#             raise UserError(_('You must define a warehouse for the company: %s.') % (company_user.name,))
#
#     location_id = fields.Many2one(
#         'stock.location', 'المخزن المجرود',
#         readonly=True, required=True,
#         states={'draft': [('readonly', False)]},
#         default=_default_location_id)
#
#
# class ProductCategoryModel(models.Model):
#     _inherit = 'product.category'
#
#     removal_strategy_id = fields.Many2one(
#         'product.removal', 'سياسه صرف المخزون',
#         help="Set a specific removal strategy that will be used regardless of the source location for this product category")







