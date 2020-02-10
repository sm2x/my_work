# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, UserError


class StockLocationModel(models.Model):
    _inherit = 'stock.location'

    capacity = fields.Float('السعه التخزينيه')
    code = fields.Char()


class PickingModel(models.Model):
    _inherit = 'stock.picking'

    # all_qty = fields.Float(compute='compute_all_qty')

    @api.multi
    def compute_all_qty(self):
        # loc_capacity = self.location_dest_id.capacity
        all_qty = sum(self.move_lines.mapped('quantity_done'))
        print(all_qty)
        print(self.location_dest_id.capacity)
        if all_qty:
            # if all_qty > loc_capacity:
            #     raise ValidationError("Location Capacity Not Available")
            if all_qty < self.location_dest_id.capacity:
                self.location_dest_id.capacity = self.location_dest_id.capacity - all_qty
            else:
                raise ValidationError("Location Capacity Not Available")


    @api.multi
    def button_validate(self):
        self.ensure_one()
        self.compute_all_qty()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))


class ProductTemplateModel(models.Model):
    _inherit = 'product.template'

    # name = fields.Char()

    @api.constrains('name')
    def _check_name(self):
        partner_rec = self.env['product.template'].search(
            [('name', '=', self.name), ('id', '!=', self.id)])
        if partner_rec:
            raise ValueError('Customer/Company Name Already Exists It Must Be Unique ')