# -*- coding: utf-8 -*-

# class ConstructionProjectTask(http.Controller):
#     @http.route('/construction_project_task/construction_project_task/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/construction_project_task/construction_project_task/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('construction_project_task.listing', {
#             'root': '/construction_project_task/construction_project_task',
#             'objects': http.request.env['construction_project_task.construction_project_task'].search([]),
#         })

#     @http.route('/construction_project_task/construction_project_task/objects/<model("construction_project_task.construction_project_task"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('construction_project_task.object', {
#             'object': obj
#         })
