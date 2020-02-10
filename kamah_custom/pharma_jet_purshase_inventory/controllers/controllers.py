# -*- coding: utf-8 -*-
from odoo import http

# class PharmaJetPurshaseInventory(http.Controller):
#     @http.route('/pharma_jet_purshase_inventory/pharma_jet_purshase_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pharma_jet_purshase_inventory/pharma_jet_purshase_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pharma_jet_purshase_inventory.listing', {
#             'root': '/pharma_jet_purshase_inventory/pharma_jet_purshase_inventory',
#             'objects': http.request.env['pharma_jet_purshase_inventory.pharma_jet_purshase_inventory'].search([]),
#         })

#     @http.route('/pharma_jet_purshase_inventory/pharma_jet_purshase_inventory/objects/<model("pharma_jet_purshase_inventory.pharma_jet_purshase_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pharma_jet_purshase_inventory.object', {
#             'object': obj
#         })