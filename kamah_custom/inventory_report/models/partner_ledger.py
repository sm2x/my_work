
from odoo import models,fields,api, _

class PartnerLedgers(models.AbstractModel):
    _inherit = "account.partner.ledger"

    def _get_template(self):
        templates = super(PartnerLedgers, self)._get_template()
        templates['line_templatess'] = 'account_reports.line_template_partner_ledger_report'
        return templates

    def _get_columns_name(self, options):
        columns = [
            {},
            {'name': _('JRNL')},
            {'name': _('Account')},
            {'name': _('Ref')},
            {'name': _('Due Date'), 'class': 'date'},
            {'name': _('Matching Number')},
            {'name': _('Initial Balance'), 'class': 'number'},
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'},
        ]


        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': _('Amount Currency'), 'class': 'number'})

        columns.append({'name': _('Balance'), 'class': 'number'})

        return columns


