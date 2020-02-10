# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api,_
from odoo.tools import float_is_zero, calendar


class OmmatAssetModify(models.TransientModel):
    _inherit = ['asset.modify']

    #     # new_date = fields.Date('Date')
    #
    @api.multi
    def modify(self):
        """ Modifies the duration of asset for calculating depreciation
        and maintains the history of old values, in the chatter.
        """
        asset_id = self.env.context.get('active_id', False)
        asset = self.env['account.asset.asset'].browse(asset_id)
        old_values = {
            'method_number': asset.method_number,
            'method_period': asset.method_period,
            'method_end': asset.method_end,
        }
        if asset.add_value:
            posted_depreciation_line_ids = asset.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(
                key=lambda l: l.depreciation_date)
            print('posted_depreciation_line_ids = ', len(posted_depreciation_line_ids))

            method_no = self.method_number+len(posted_depreciation_line_ids)
        else:
            method_no = self.method_number

        asset_vals = {
            'method_number': method_no,
            'method_period': self.method_period,
            'method_end': self.method_end,
        }
        asset.write(asset_vals)
        asset.compute_depreciation_board()
        tracked_fields = self.env['account.asset.asset'].fields_get(['method_number', 'method_period', 'method_end'])
        changes, tracking_value_ids = asset._message_track(tracked_fields, old_values)
        if changes:
            asset.message_post(subject=_('Depreciation board modified'), body=self.name,
                               tracking_value_ids=tracking_value_ids)
        return {'type': 'ir.actions.act_window_close'}


class OmmatAccountAssetAsset(models.Model):
    _inherit = ['account.asset.asset']
# TODO child domain=,('id', '!=', False)
    child_id = fields.Many2one('account.asset.asset', string='Child')
    # , domain = ([('loss_type', 'in', ['quality', 'availability'])])
    parent_id = fields.Many2one('account.asset.asset', string='Parent', compute='get_parent')

    state = fields.Selection(selection_add=[('stop', 'Stop')])

    total_depreciation = fields.Float(compute='get_total_depreciation', string="Total Depreciation")

    total_accumulated_depreciation = fields.Float(compute='get_total_depreciation',
                                                  string="Total Accumulated Depreciation")

    total_asset_amount = fields.Float(compute='get_total_asset_amount', string="Total Asset Amount")

    new_value = fields.Float('Re-Evaluation', compute='get_new_value')
    add_value = fields.Boolean('Add Value', copy=False)

    is_parent = fields.Boolean('Parent')
    is_child = fields.Boolean('Child', compute='get_parent')
    # child = fields.Char('Child', store=True)

    @api.multi
    def get_parent(self):
        for rec in self:
            parent = rec.env['account.asset.asset'].search([('child_id','=', self.id)])
            if parent:
                rec.parent_id = parent
                rec.is_child = True
                # rec.state = 'stop'



    # @api.multi
    # @api.depends('parent_id')
    # def get_new_value(self):
    #     for rec in self:
    #         if rec.parent:
    #             rec.is_child = True

    @api.multi
    @api.onchange('child_id')
    def get_new_value(self):
        for rec in self:
            if rec.child_id:

                rec.add_value = True
                rec.new_value = rec.child_id.value_residual
            else:
                rec.add_value = False



    @api.multi
    def compute_depreciation_board(self):
        self.ensure_one()

        posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(
            key=lambda l: l.depreciation_date)
        unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

        if self.value_residual != 0.0:
            if self.add_value:
                amount_to_depr = residual_amount = self.value_residual+self.new_value
            else:
                amount_to_depr = residual_amount = self.value_residual

            # if we already have some previous validated entries, starting date is last entry + method period
            if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                last_depreciation_date = fields.Date.from_string(posted_depreciation_line_ids[-1].depreciation_date)
                depreciation_date = last_depreciation_date+relativedelta(months=+self.method_period)
            else:
                # depreciation_date computed from the purchase date
                depreciation_date = self.date
                if self.date_first_depreciation == 'last_day_period':
                    # depreciation_date = the last day of the month
                    depreciation_date = depreciation_date+relativedelta(day=31)
                    # ... or fiscalyear depending the number of period
                    if self.method_period == 12:
                        depreciation_date = depreciation_date+relativedelta(month=self.company_id.fiscalyear_last_month)
                        depreciation_date = depreciation_date+relativedelta(day=self.company_id.fiscalyear_last_day)
                        if depreciation_date < self.date:
                            depreciation_date = depreciation_date+relativedelta(years=1)
                elif self.first_depreciation_manual_date and self.first_depreciation_manual_date != self.date:
                    # depreciation_date set manually from the 'first_depreciation_manual_date' field
                    depreciation_date = self.first_depreciation_manual_date

            total_days = (depreciation_date.year % 4) and 365 or 366
            month_day = depreciation_date.day
            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)

            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                sequence = x+1
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number,
                                                    posted_depreciation_line_ids, total_days, depreciation_date)
                amount = self.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount
                vals = {
                    'amount': amount,
                    'asset_id': self.id,
                    'sequence': sequence,
                    'name': (self.code or '')+'/'+str(sequence),
                    'remaining_value': residual_amount,
                    'depreciated_value': self.value-(self.salvage_value+residual_amount),
                    'depreciation_date': depreciation_date,
                }
                commands.append((0, False, vals))

                depreciation_date = depreciation_date+relativedelta(months=+self.method_period)

                if month_day > 28 and self.date_first_depreciation == 'manual':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=min(max_day_in_month, month_day))

                # datetime doesn't take into account that the number of days is not the same for each month
                if not self.prorata and self.method_period % 12 != 0 and self.date_first_depreciation == 'last_day_period':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=max_day_in_month)

        self.write({'depreciation_line_ids': commands})

        return True

    @api.multi
    @api.onchange('depreciation_line_ids')
    def get_total_depreciation(self):
        # self.ensure_one()
        for asset in self:
            for depreciation_line in asset.depreciation_line_ids:
                for move_line in depreciation_line.move_id.line_ids:
                    self.total_depreciation += move_line.debit
                    self.total_accumulated_depreciation += move_line.credit

    @api.multi
    # @api.depends('depreciation_line_ids')
    def get_total_asset_amount(self):
        for rec in self:
            if rec.new_value:
                rec.total_asset_amount = (rec.value-rec.salvage_value)+ rec.new_value
            else:
                rec.total_asset_amount = (rec.value-rec.salvage_value)