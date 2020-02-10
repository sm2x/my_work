# -*- coding: utf-8 -*-
from odoo import http

# class AssetsManagement(http.Controller):
#     @http.route('/assets_management/assets_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/assets_management/assets_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('assets_management.listing', {
#             'root': '/assets_management/assets_management',
#             'objects': http.request.env['assets_management.assets_management'].search([]),
#         })

#     @http.route('/assets_management/assets_management/objects/<model("assets_management.assets_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('assets_management.object', {
#             'object': obj
#         })