# -*- coding: utf-8 -*-
from odoo import http

# class NaseejReturn(http.Controller):
#     @http.route('/naseej_return/naseej_return/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/naseej_return/naseej_return/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('naseej_return.listing', {
#             'root': '/naseej_return/naseej_return',
#             'objects': http.request.env['naseej_return.naseej_return'].search([]),
#         })

#     @http.route('/naseej_return/naseej_return/objects/<model("naseej_return.naseej_return"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('naseej_return.object', {
#             'object': obj
#         })