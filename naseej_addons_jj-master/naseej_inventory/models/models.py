# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare


class NaseejStockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # move_line = fields.Many2one('stock.move.line')
    old_lot = fields.Many2one('stock.production.lot', 'Old Lot')
    old_qty = fields.Float('Old Quantity')


# class NaseejStockMove(models.Model):
#     _inherit = 'stock.move'
#
#     def _prepare_move_line_vals2(self):
#         self.ensure_one()
#         test_return = self.picking_id.picking_type_id.return_loc
#         if test_return:
#             vals = []
#
#             for line in self.picking_id.move_lines.move_line_ids:
#                 vals.append((0, 0, {
#                     'location_id': line.location_dest_id.id,
#                     'location_dest_id': line.location_id.id,
#                     'old_lot': line.lot_id.id,
#                     'old_qty': line.qty_done,
#                     'lot_name': _("rt %s") % line.old_lot.name,
#                     'product_uom_qty': line.product_uom_qty
#                 }))
#
#     def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
#         self.ensure_one()
#
#         # apply putaway
#
#         location_dest_id = self.location_dest_id.get_putaway_strategy(self.product_id).id or self.location_dest_id.id
#
#         vals = {
#             'move_id': self.id,
#             'product_id': self.product_id.id,
#             'product_uom_id': self.product_uom.id,
#             'location_id': self.location_id.id,
#             'location_dest_id': location_dest_id,
#             'picking_id': self.picking_id.id,
#         }
#         if quantity:
#             uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom,
#                                                                     rounding_method='HALF-UP')
#             uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id,
#                                                                                   rounding_method='HALF-UP')
#             rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#             if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
#                 vals = dict(vals, product_uom_qty=uom_quantity)
#             else:
#                 vals = dict(vals, product_uom_qty=quantity, product_uom_id=self.product_id.uom_id.id)
#         if reserved_quant:
#             vals = dict(
#                 vals,
#                 location_id=reserved_quant.location_id.id,
#                 lot_id=reserved_quant.lot_id.id or False,
#                 old_lot=reserved_quant.lot_id.id,
#                 package_id=reserved_quant.package_id.id or False,
#                 owner_id=reserved_quant.owner_id.id or False,
#             )
#
#             # vals = dict(
#             #     vals,
#             #     {
#             #         'location_id': line.location_dest_id.id,
#             #         'location_dest_id': line.location_id.id,
#             #         'old_lot': line.lot_id.id,
#             #         'old_qty': line.qty_done,
#             #         'lot_name': _("rt %s") % line.old_lot.name,
#             #         'product_uom_qty': line.product_uom_qty
#             #     }
#             #     location_id=reserved_quant.location_id.id,
#             #     lot_id=reserved_quant.lot_id.id or False,
#             #     old_lot=reserved_quant.lot_id.id,
#             #     package_id=reserved_quant.package_id.id or False,
#             #     owner_id=reserved_quant.owner_id.id or False,
#             # )
#         return vals


class NaseejInventory(models.Model):
    _inherit = 'stock.picking.type'

    internal_loc = fields.Boolean('Is Internal?')
    return_loc = fields.Boolean('Is Return?')

    internal_location = fields.Many2one('stock.location', string='Destination Transfer Location')
    return_location = fields.Many2one('stock.location', string='Return Transfer Location')

    internal_operation_type = fields.Many2one('stock.picking.type', string='Internal Operation Type')
    nas_return_operation_type = fields.Many2one('stock.picking.type', string='NReturn Operation Type')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pack_picking_id = fields.Many2one('stock.picking', 'Pack Picking')
    return_picking_id = fields.Many2one('stock.picking', 'Return Picking')
    show_button_generate = fields.Boolean(string="show", default=True)
    after_click_button_generate = fields.Boolean(string="click", default=True)
    check_operation_type = fields.Boolean(string="click", default=True)
    nas_move_lines = fields.One2many('stock.move.line', 'picking_id', 'Moves')

    @api.onchange('picking_type_id')
    def _check_operation_type(self):
        for pick in self:
            if pick.picking_type_id.code != 'internal':
                self.check_operation_type = False

    @api.onchange('picking_type_id')
    def show_generate_btn(self):
        for pick in self:
            if not pick.picking_type_id.internal_loc:
                self.show_button_generate = False

    def generate_receipt_order(self):
        for rec in self:
            pick = rec.copy()
            internal_picking_type = rec.picking_type_id.internal_operation_type
            pick_dest_location = rec.picking_type_id.internal_location
            pick.write({'picking_type_id': internal_picking_type.id,
                        'location_id': rec.location_dest_id.id,
                        'location_dest_id': pick_dest_location.id, })
            for line in pick.move_lines:
                line.write({
                    'picking_type_id': internal_picking_type.id,
                    'picking_id': pick.id,
                    'location_id': rec.location_dest_id.id,
                    'location_dest_id': pick_dest_location.id
                })

            pick.action_confirm()
            pick.action_assign()
            pick.show_button_generate = False
            rec.after_click_button_generate = False
            rec.pack_picking_id = pick.id

    def generate_return_picking(self):
        for rec in self:

            pick = rec.copy()
            return_picking_type = rec.picking_type_id.nas_return_operation_type
            move_lines = []

            for line in self.move_lines.move_line_ids:
                move_lines.append((0, 0, {
                    'location_id': line.location_dest_id.id,
                    'location_dest_id': line.location_id.id,
                    'old_lot': line.lot_id.id,
                    'old_qty': line.qty_done,
                    'lot_name': _("rt %s") % line.old_lot.name,
                    'product_uom_qty': line.product_uom_qty
                }))
            pick.write({
                'picking_type_id': return_picking_type.id,
                'origin': _("Return of %s") % rec.name,
                'location_id': rec.location_dest_id.id,
                'location_dest_id': rec.location_id.id,
                'nas_move_lines': move_lines
            })

            for line in pick.move_lines:
                line.write({
                    'picking_type_id': return_picking_type.id,
                    'picking_id': pick.id,
                    'location_id': rec.location_dest_id.id,
                    'location_dest_id': rec.location_id.id,
                    # 'move_line_ids': move_lines
                })

            pick.action_confirm()
            # pick.action_assign()
            # pick.button_validate()
            # pick.show_button_generate = False
            # self.after_click_button_generate = False
            rec.return_picking_id = pick.id
