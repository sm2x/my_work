# -*- coding: utf-8 -*-
from odoo import http

# class OmmatCatalogue(http.Controller):
#     @http.route('/ommat_catalogue/ommat_catalogue/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ommat_catalogue/ommat_catalogue/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ommat_catalogue.listing', {
#             'root': '/ommat_catalogue/ommat_catalogue',
#             'objects': http.request.env['ommat_catalogue.ommat_catalogue'].search([]),
#         })

#     @http.route('/ommat_catalogue/ommat_catalogue/objects/<model("ommat_catalogue.ommat_catalogue"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ommat_catalogue.object', {
#             'object': obj
#         })