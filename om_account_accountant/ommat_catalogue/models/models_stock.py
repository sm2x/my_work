# -*- coding: utf-8 -*-


from odoo import models, fields, api , _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar
from odoo.tools import float_compare, float_is_zero


class OmmatStockLoc(models.Model):
    _inherit = 'stock.location'

    type_l_b = fields.Selection([('land', 'Land')
                                , ('bat', 'Battery')], copy=False, default='land', string="Loc Type 1")

    type_f_p = fields.Selection([('farm', 'Farming')
                                , ('pro', 'Production')], copy=False, default='farm', string="Loc Type 2")

class newaccountsProductCategory(models.Model):
    _inherit = 'product.category'

    other_stock_account_input_id = fields.Many2one(
        'account.account', 'Other Purchase Stock Input Account', company_dependent=True,
        domain=[('deprecated', '=', False)])
    other_stock_account_output_id = fields.Many2one(
        'account.account', 'Other Sale Stock Output Account', company_dependent=True,
        domain=[('deprecated', '=', False)])


class stock_move_change_ommat(models.Model):
    _inherit = 'stock.move'


    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):

        if self.product_id:

            product_categ=self.product_id.categ_id

            if self.sale_line_id and product_categ.other_stock_account_output_id:

                if debit_account_id ==product_categ.property_stock_account_output_categ_id.id:
                    debit_account_id=product_categ.other_stock_account_output_id.id
                elif credit_account_id ==product_categ.property_stock_account_output_categ_id.id:
                    credit_account_id=product_categ.other_stock_account_output_id.id

            elif self.purchase_line_id and product_categ.other_stock_account_input_id:

                if debit_account_id ==product_categ.property_stock_account_input_categ_id.id:
                    debit_account_id=product_categ.other_stock_account_input_id.id
                elif credit_account_id ==product_categ.property_stock_account_input_categ_id.id:
                    credit_account_id=product_categ.other_stock_account_input_id.id

        res =super(stock_move_change_ommat,self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
        return res


class PriceUnitDigits(models.Model):
    _inherit = 'purchase.order.line'

    price_unit = fields.Float(string='Unit Price', required=True, digits=(16, 5))


class PriceUnitDigitsInvoice(models.Model):
    _inherit = 'account.invoice.line'

    price_unit = fields.Float(string='Unit Price', required=True, digits=(16, 5))


class payments_check_create(models.Model):

    _name = 'native.payments.check.create'
    _order = 'check_number asc'

    check_number = fields.Char(string=_("Check number"),required=True)
    check_date = fields.Date(string=_('Check Date'),required=True)
    amount = fields.Float(string=_('Amount'),required=True)
    bank = fields.Many2one('res.bank',string=_("Check Bank Name"))
    dep_bank = fields.Many2one('res.bank',string=_("Depoist Bank"))
    nom_pay_id = fields.Many2one('normal.payments')


class approve_check_lines(models.Model):

    _name = 'appove.check.lines'

    check_number = fields.Char()
    check_id = fields.Integer()
    check_amt = fields.Float()
    paid_amt = fields.Float()
    open_amt = fields.Float()


class account_journal(models.Model):

    _inherit = 'account.journal'

    payment_subtype = fields.Selection([('issue_check',_('Issued Checks')),('rece_check',_('Received Checks'))],string="Payment Subtype")


class OmmatAccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.v8
    def get_invoice_line_account(self, type, product, fpos, company):
        if product.categ_id.other_stock_account_input_id:
            # print('Innnnnnn')
            accounts = {
                'income': product.property_account_income_id or product.categ_id.property_account_income_categ_id,
                'expense': product.categ_id.other_stock_account_input_id
            }
        else:
            accounts = product.product_tmpl_id.get_product_accounts(fpos)

        if type in ('out_invoice', 'out_refund'):
            return accounts['income']
        return accounts['expense']

