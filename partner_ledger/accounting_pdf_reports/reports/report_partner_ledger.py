# -*- coding: utf-8 -*-

import time

from odoo import api, models, _
from odoo.exceptions import UserError


class ReportPartnerLedger(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_partnerledger'

    # accounting_pdf_reports.
    # partner_ids = fields.Many2many('res.partner')

    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        invoice = self.env['account.invoice']
        payment = self.env['account.payment']
        check_payment = self.env['normal.payments']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + \
                 query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date,
             "account_move_line".invoice_id,"account_move_line".payment_id,
             "account_move_line".normal_pay_id,
              j.code, acc.code as a_code, acc.name as a_name,
             "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit,
              "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id,
               c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_invoice inv ON ("account_move_line".invoice_id=inv.id)
            LEFT JOIN account_payment pay ON ("account_move_line".payment_id=pay.id)
            LEFT JOIN normal_payments chpay ON("account_move_line".normal_pay_id=chpay.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        # LEFT JOIN ormal.payments chpay ON("account_move_line".jebal_con_pay_id = chpay.id)

        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0

        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']

        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            # print('move name', r['displayed_name'])

            str = r['displayed_name'].find('-')
            ref = r['displayed_name'][0:str]
            # invoice = self.env['account.invoice'].search([('number', '=', ref)])
            # print(invoice.number)
            # for line in invoice.invoice_line_ids:
            #     # print(line.name)
            #     inv_lines.append({
            #         "product_id": line.product_id.id,
            #         "quantity": line.quantity
            #     })

            # print('l = ', inv_lines)

            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            r['invoice_id'] = invoice.browse(r.get('invoice_id'))
            r['payment_id'] = payment.browse(r.get('payment_id'))
            r['normal_pay_id'] = check_payment.browse(r.get('normal_pay_id'))
            # print('line name', r['normal_pay_id'].name)

            full_account.append(r)
        return full_account

    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + \
                 query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        # print('tttttt', data['form'].get('custom_partners'))

        if contemp is not None:
            result = contemp[0] or 0.0

        # print('oooooooo',data['form']['partner_ids'])

        # self.partner_ids=p.id

        # for pp in self.partner_ids:
        #     print('pp name',pp.name)

        # if data['form']['custom_partners']:
        #     result = data['form']['partner_ids']
        # else:
        #     if contemp is not None:
        #         result = contemp[0] or 0.0

        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        data['computed'] = {}

        obj_partner = self.env['res.partner']
    # partner_ids = fields.Many2many('res.partner')

        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        # print('ps.type', type(partner_ids))
        # print(partner_ids)
        if data['form'].get('custom_partners'):
            ps = data['form']['partner_ids']
            print(ps)
            partner_ids = [sub['id'] for sub in ps]
            print(partner_ids)
            partners = obj_partner.browse(partner_ids)
            # ps = data['form']['partner_ids']
            # print('ps.type', type(ps))
            # for p in partner_ids:
            #
            #     print('pp name', p['id'])
            #     p = self.env['res.partner'].search([('id', '=', p['id'])])
            #     print('pp name', p.name)

        else:
            partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
            print(partner_ids)
            partners = obj_partner.browse(partner_ids)

        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))

        return {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
        }
