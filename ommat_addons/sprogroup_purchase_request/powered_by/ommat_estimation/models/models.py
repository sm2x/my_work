from odoo import models, fields


# import odoo.addons.decimal_precision as dp
# from odoo.exceptions import UserError

class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    lot_no_omat = fields.Many2one('stock.production.lot', string='Lot/Serial Number')


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    lot_no_omat = fields.Many2one('stock.production.lot', string='Lot/Serial Number')


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    lot_no_omat = fields.Many2one('stock.production.lot', string='Lot/Serial Number')


# class HelpdeskTicketInherit(models.Model):
#     _inherit = 'helpdesk.ticket'

    # lot_no_omat = fields.Many2one('stock.production.lot', string='Lot/Serial Number')


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    lot_no_omat = fields.Many2one('stock.production.lot', string='Lot/Serial Number')
