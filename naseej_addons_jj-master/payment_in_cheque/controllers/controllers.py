# -*- coding: utf-8 -*-
from odoo import http

# class PaymentInCheque(http.Controller):
#     @http.route('/payment_in_cheque/payment_in_cheque/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_in_cheque/payment_in_cheque/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_in_cheque.listing', {
#             'root': '/payment_in_cheque/payment_in_cheque',
#             'objects': http.request.env['payment_in_cheque.payment_in_cheque'].search([]),
#         })

#     @http.route('/payment_in_cheque/payment_in_cheque/objects/<model("payment_in_cheque.payment_in_cheque"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_in_cheque.object', {
#             'object': obj
#         })