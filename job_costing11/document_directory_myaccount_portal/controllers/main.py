# -*- coding: utf-8 -*-

import base64

import werkzeug
import werkzeug.utils
import werkzeug.wrappers
from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request


def binary_content(xmlid=None, model='ir.attachment', id=None, field='datas', unique=False,
                   filename=None, filename_field='datas_fname', download=False, mimetype=None,
                   default_mimetype='application/octet-stream', access_token=None, env=None):
    return request.registry['ir.http'].binary_content(
        xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
        filename_field=filename_field, download=download, mimetype=mimetype,
        default_mimetype=default_mimetype, access_token=access_token, env=request.env(user=SUPERUSER_ID))


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        return values

    @http.route(['/my/documents'], type='http', auth="user", website=True)
    def portal_my_documents(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        directorys = request.env['document.directory'].sudo().search([])
        values.update({'directorys': directorys})
        return request.render("document_directory_myaccount_portal.portal_my_document_directory", values)

    @http.route(['/my/directory_documents/<int:directory>'], type='http', auth="public", website=True)
    def portal_directory_page(self, directory=None, access_token=None, **kw):
        user = request.env.user
        directory_id = request.env['document.directory'].sudo().browse(directory)
        if directory_id == request.env.ref('document_directory_myaccount_portal.menu_directory_other_document'):
            attachment_ids = request.env['ir.attachment'].sudo().search(
                [('directory_id', '=', False), ('partner_ids', 'in', user.partner_id.id)])
        else:
            attachment_ids = request.env['ir.attachment'].sudo().search(
                [('directory_id', '=', directory_id.id), ('partner_ids', 'in', user.partner_id.id)])

        #         document_user_group =  request.env.ref('document_directory_extension_security.group_document_user')
        #         document_manager_group =  request.env.ref('document_directory_extension.group_document_manager')
        #         employee_group =  request.env.ref('base.group_user')

        #         document_user =  user.id in document_user_group.users.ids and True or False
        #         document_manager = user.id in document_manager_group.users.ids and True or False
        #         employee = user.id in employee_group.users.ids and True or False
        #
        #         if employee and not (document_user and document_manager):
        #             attachment_ids = attachment_ids.filtered(lambda i:i.create_uid == request.env.user)

        values = {'attachments': attachment_ids, 'directory': directory_id}
        return request.render("document_directory_myaccount_portal.portal_my_directory_document", values)

    @http.route(['/my/directory_doc/<int:attachment>'], type='http', auth="public", website=True)
    def portal_directory_attachment_page(self, attachment=None, access_token=None, **kw):
        attachment_id = request.env['ir.attachment'].sudo().browse(attachment)
        values = {
            'attachment': attachment_id,
        }
        return request.render("document_directory_myaccount_portal.portal_attachment_page", values)

    @http.route(['/my/document',
                 '/my/document/<string:xmlid>',
                 '/my/document/<string:xmlid>/<string:filename>',
                 '/my/document/<int:id>',
                 '/my/document/<int:id>/<string:filename>',
                 '/my/document/<int:id>-<string:unique>',
                 '/my/document/<int:id>-<string:unique>/<string:filename>',
                 '/my/document/<string:model>/<int:id>/<string:field>',
                 '/my/document/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='datas_fname', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None):
        status, headers, content = binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            access_token=access_token)
        if status == 304:
            response = werkzeug.wrappers.Response(status=status, headers=headers)
        elif status == 301:
            return werkzeug.utils.redirect(content, code=301)
        elif status != 200:
            response = request.not_found()
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
        if token:
            response.set_cookie('fileToken', token)
        return response
