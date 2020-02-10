# -*- coding: utf-8 -*-
from odoo import http

# class PriceUnitDigits(http.Controller):
#     @http.route('/price_unit_digits/price_unit_digits/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/price_unit_digits/price_unit_digits/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('price_unit_digits.listing', {
#             'root': '/price_unit_digits/price_unit_digits',
#             'objects': http.request.env['price_unit_digits.price_unit_digits'].search([]),
#         })

#     @http.route('/price_unit_digits/price_unit_digits/objects/<model("price_unit_digits.price_unit_digits"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('price_unit_digits.object', {
#             'object': obj
#         })