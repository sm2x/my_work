# -*- coding: utf-8 -*-

from odoo import fields, models, _


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.common.partner.report"
    _name = "account.report.partner.ledger"
    _description = "Account Partner Ledger"

    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on report if the "
                                          "currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')

    # TODO Editing Here
    custom_partners = fields.Boolean('Custom Partners?')
    partner_ids = fields.Many2many('res.partner')

    def _print_report(self, data):
        partners=[]
        for p in self.partner_ids:
            partners.append({
                    'id': p.id,})
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'partner_ids': partners, 'custom_partners': self.custom_partners, 'amount_currency': self.amount_currency})
        return self.env.ref('accounting_pdf_reports.action_report_partnerledger').report_action(self, data=data)
