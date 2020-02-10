# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SellAssetsWizard(models.TransientModel):
    _name = "sell.assets.wizard"

    sell_total_depreciation = fields.Float(compute='sell_get_total_depreciation', string="Total Depreciation")
    sell_total_accumulated_depreciation = fields.Float(compute='sell_get_total_depreciation',
                                                       string="Total Accumulated  Depreciation")
    sale_price = fields.Float(string='Sale Price')
    net_asset_amount = fields.Float(string="Net Asset Amount", compute='get_net_asset_amount')
    net_profit = fields.Float(compute='get_net_profit', string="Net Profit/loss")
    total_asset_amount = fields.Float(compute='get_total_asset_amount', string="Total Asset Amount")
    sale_account = fields.Many2one('account.account', string="Sale Account")
    net_profit_account = fields.Many2one('account.account', string="Net Profit/loss Account")

    @api.multi
    @api.onchange('sale_price')
    def get_total_asset_amount(self):
        self.ensure_one()
        if self.env.context.get('active_id'):
            asset = self.env['account.asset.asset'].browse(self.env.context.get('active_id'))
            if asset.add_value:
                self.total_asset_amount = asset.total_asset_amount+asset.new_value
            else:
                self.total_asset_amount = asset.total_asset_amount

            # self.total_asset_amount = asset.total_asset_amount

    @api.multi
    @api.onchange('sale_price')
    def sell_get_total_depreciation(self):
        self.ensure_one()
        if self.env.context.get('active_id'):
            asset = self.env['account.asset.asset'].browse(self.env.context.get('active_id'))
            self.sell_total_depreciation = asset.total_depreciation
            self.sell_total_accumulated_depreciation = asset.total_accumulated_depreciation

    @api.multi
    @api.onchange('sale_pric')
    def get_net_asset_amount(self):
        self.ensure_one()
        if self.env.context.get('active_id'):
            asset = self.env['account.asset.asset'].browse(self.env.context.get('active_id'))
            unposted_depreciation_line_ids = asset.depreciation_line_ids.filtered(lambda x: not x.move_check)
            amount = sum(line.amount for line in unposted_depreciation_line_ids)
            if asset.add_value:
                self.net_asset_amount = amount
            else:
                self.net_asset_amount = asset.value_residual

    @api.multi
    @api.onchange('sale_price')
    def get_net_profit(self):
        self.ensure_one()
        # if self.env.context.get('active_id'):
        #     asset = self.env['account.asset.asset'].browse(self.env.context.get('active_id'))
        self.net_profit = self.sale_price-self.net_asset_amount

    @api.multi
    # @api.depends('depreciation_line_ids')
    def sell_asset(self):
        # self.ensure_one()
        print('sssssssssss')
        for rec in self:
            if rec.env.context.get('active_id'):
                asset = rec.env['account.asset.asset'].browse(rec.env.context.get('active_id'))
                date = fields.Date.from_string(fields.Date.today())
                debit_depreciation_acc = asset.category_id.account_depreciation_id
                credit_asset_acc = asset.category_id.account_asset_id
                debit_sale_acc = rec.sale_account
                net_profit_acc = rec.net_profit_account
                journal_id = asset.category_id.journal_id
                company = rec.env.user.company_id
                account_move = rec.env['account.move']

                if rec.net_profit >= 0:
                    print('rec.net_profit >= 0')
                    line_ids = [
                        (0, 0,
                         {'journal_id': journal_id.id,
                          'account_id': debit_depreciation_acc.id,
                          'name': asset.name,
                          # 'amount_currency': -cheque_obj.amount_currency or False,
                          'currency_id': company.currency_id.id,
                          'debit': rec.sell_total_depreciation}),

                        (0, 0, {'journal_id': journal_id.id,
                                'account_id': credit_asset_acc.id,
                                # 'partner_id': cheque_obj.partner_id.id,
                                'name': asset.name,
                                # 'amount_currency': cheque_obj.amount_currency or False,
                                'currency_id': company.currency_id.id,
                                'credit': rec.total_asset_amount}),

                        (0, 0, {'journal_id': journal_id.id,
                                'account_id': debit_sale_acc.id,
                                # 'partner_id': cheque_obj.partner_id.id,
                                'name': asset.name,
                                # 'amount_currency': cheque_obj.amount_currency or False,
                                'currency_id': company.currency_id.id,
                                'debit': rec.sale_price}),

                        ((0, 0, {
                            'journal_id': journal_id.id,
                            'account_id': net_profit_acc.id,
                            # 'partner_id': cheque_obj.partner_id.id,
                            'name': asset.name,
                            # 'amount_currency': cheque_obj.amount_currency or False,
                            'currency_id': company.currency_id.id,
                            'credit': rec.net_profit}))

                    ]

                else:
                    print('else')
                    line_ids = [
                        (0, 0,
                         {'journal_id': journal_id.id,
                          'account_id': debit_depreciation_acc.id,
                          'name': asset.name,
                          # 'amount_currency': -cheque_obj.amount_currency or False,
                          'currency_id': company.currency_id.id,
                          'debit': rec.sell_total_depreciation}),

                        (0, 0, {'journal_id': journal_id.id,
                                'account_id': credit_asset_acc.id,
                                # 'partner_id': cheque_obj.partner_id.id,
                                'name': asset.name,
                                # 'amount_currency': cheque_obj.amount_currency or False,
                                'currency_id': company.currency_id.id,
                                'credit': rec.total_asset_amount}),

                        (0, 0, {'journal_id': journal_id.id,
                                'account_id': debit_sale_acc.id,
                                # 'partner_id': cheque_obj.partner_id.id,
                                'name': asset.name,
                                # 'amount_currency': cheque_obj.amount_currency or False,
                                'currency_id': company.currency_id.id,
                                'debit': rec.sale_price}),
                        ((0, 0, {
                            'journal_id': journal_id.id,
                            'account_id': net_profit_acc.id,
                            # 'partner_id': cheque_obj.partner_id.id,
                            'name': asset.name,
                            # 'amount_currency': cheque_obj.amount_currency or False,
                            'currency_id': company.currency_id.id,
                            # -
                            'debit': -rec.net_profit}))
                    ]
                vals = {
                    'journal_id': journal_id.id,
                    'ref': asset.name,
                    'date': date,
                    'line_ids': line_ids,
                }
                account_move.create(vals)
                rec.clicked = True
