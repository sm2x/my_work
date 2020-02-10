# -*- coding: utf-8 -*-
from odoo import http

# class NaseejPosOrder(http.Controller):
#     @http.route('/naseej_pos_order/naseej_pos_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/naseej_pos_order/naseej_pos_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('naseej_pos_order.listing', {
#             'root': '/naseej_pos_order/naseej_pos_order',
#             'objects': http.request.env['naseej_pos_order.naseej_pos_order'].search([]),
#         })

#     @http.route('/naseej_pos_order/naseej_pos_order/objects/<model("naseej_pos_order.naseej_pos_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('naseej_pos_order.object', {
#             'object': obj
#         })