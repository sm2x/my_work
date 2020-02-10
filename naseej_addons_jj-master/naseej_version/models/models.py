from odoo import models, fields, api
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from datetime import date

# from itertools import groupby

# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


class NaseejProjectSerialVariantInherit(models.Model):
    _inherit = 'product.product'

    default_code = fields.Char('Internal Reference', index=True, readonly='True')
    # fr_serial = fields.Char('First Serial Copy Reference', index=True,store='True')

    _sql_constraints = [
        ('internal_reference_unique', 'unique(default_code)', "Internal Reference Already Exists It Must Be Unique !"),
    ]

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('increment_id_of_serial_of_reports_forms')
        vals['default_code'] = sequence
        result = super(NaseejProjectSerialVariantInherit, self).create(vals)
        return result


class NaseejProjectSerialfieldInherit(models.Model):
    _inherit = 'stock.move.line'

    first_serial = fields.Char(string='First Serial', default=False)
    second_serial = fields.Char(string='Second Serial', related='move_id.internal_reference_code')
    third_serial = fields.Char(store='True', string='Third Serial',
                               default=lambda self: self.env['ir.sequence'].next_by_code('stockmoveline'),
                               readonly='True')

    lot_name = fields.Char('Lot/Serial Number Name', store='True', compute='_compute_lot_serial')

    _sql_constraints = [
        ('total_lot_name_unique', 'unique(lot_name)', "Lot/Serial Number Already Exists It Must Be Unique !"),
    ]

    @api.one
    @api.depends('first_serial', 'second_serial', 'third_serial')
    def _compute_lot_serial(self):
        if self.first_serial and self.second_serial and self.third_serial:
            self.lot_name = (str(self.first_serial)+'/'+str(self.second_serial)+'/'+str(self.third_serial))


class NaseejProjectSerialfieInherit(models.Model):
    _inherit = 'stock.move'

    internal_reference_code = fields.Char(string='Internal serial ref', related='product_id.default_code')


class NaseejProjectSerialstockpickingfieInherit(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(('Please add some items to move.'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(
            float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids)
        no_reserved_quantities = all(
            float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in
            self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError((
                'You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if self.name == 'Receipts':
                        if not line.first_serial:
                            raise UserError(
                                ('You need to supply a First/Serial number for product %s.') % product.display_name)

                    elif not line.lot_name and not line.lot_id:
                        raise UserError(
                            ('You need to supply a Lot/Serial number for product %s.') % product.display_name)

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': ('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        return





# class NaseejReturn(models.TransientModel):
#     _inherit = 'stock.return.picking'
#
#     def _prepare_move_default_values(self, return_line, new_picking):
#         vals = {
#             'product_id': return_line.product_id.id,
#             'product_uom_qty': return_line.quantity,
#             'product_uom': return_line.product_id.uom_id.id,
#             'picking_id': new_picking.id,
#             'state': 'draft',
#             'date_expected': fields.Datetime.now(),
#             'location_id': return_line.move_id.location_dest_id.id,
#             'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
#             'picking_type_id': new_picking.picking_type_id.id,
#             'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
#             'origin_returned_move_id': return_line.move_id.id,
#             'procure_method': 'make_to_stock',
#             'lot_id': return_line.product_lots.id,
#         }
#         return vals
