# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class ommat_catalogue(models.Model):
    _name = 'ommat.catalogue'
    _description = "Catalogue"
    _rec_name = 'flock_id'

    flock_id = fields.Many2one('flock.model', string="القطيع", required=True)
    # lot_id = fields.Many2one(related='flock_id.lot_id', string='رقم القطيع')
    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status', default='in_progress')

    product_id_f = fields.Many2one('product.template', string='الصنف -انثى')
    product_id_fm = fields.Many2one('product.template', string='الصنف -انثى منتج', required=True)
    product_id_m = fields.Many2one('product.template', string='الصنف -ذكر')

    dynasty = fields.Many2one(related='flock_id.dynasty', string='السلاله')

    flock_num = fields.Integer('عدد القطيع', required=True)
    land_f_num = fields.Integer('عدد الاناث ارضى', required=True)
    land_m_num = fields.Integer('عدد الذكور أرضى', required=True)
    bat_f_num = fields.Integer('عدد الاناث بطاريات', required=True)
    bat_m_num = fields.Integer('بطاريات عدد الذكور', required=True)

    date_from = fields.Date('من', required=True)
    date_to = fields.Date('إلى')

    land_week_ids = fields.One2many('land.week', 'l_catalogue_id', string='أرضى', readonly=True)
    bat_week_ids = fields.One2many('bat.week', 'b_catalogue_id', string='بطاريات', readonly=True)

    w_land_week_ids = fields.One2many('land.week.w', 'l_catalogue_id_ww', readonly=True)
    w_bat_week_ids = fields.One2many('bat.week.w', 'b_catalogue_id_ww', readonly=True)

    last_rested_ommat_fl = fields.Float(compute='get_last_rested_l', string='عدد الامهات فى نهاية القطيع -اناث -أ',
                                        digits=(16, 4))
    last_rested_ommat_ml = fields.Float(compute='get_last_rested_l', string='عدد الامهات فى نهاية القطيع -ذكور -أ',
                                        digits=(16, 4))
    weight_avg_l = fields.Float('متوسط وزن الام -أ')
    kilo_price_l = fields.Float('سعر الكيلو -أ')
    e_value_l = fields.Float(compute='get_e_value', string='القيمه المقدره')

    last_rested_ommat_fb = fields.Float(compute='get_last_rested_b', string='عدد الامهات فى نهاية القطيع ',
                                        digits=(16, 4))
    last_rested_ommat_mb = fields.Float(compute='get_last_rested_b', string='عدد الامهات فى نهاية القطيع ',
                                        digits=(16, 4))
    weight_avg_b = fields.Float('متوسط وزن الام -ب')
    kilo_price_b = fields.Float('سعر الكيلو -ب')
    e_value_b = fields.Float(compute='get_e_value', string='القيمه المقدره')

    e_value_acc_debit = fields.Many2one('account.account', string='حساب مدين', required=True)
    e_value_acc_credit = fields.Many2one('account.account', string='حساب دائن', required=True)
    depreciation_account = fields.Many2one('account.account', string='حساب الاهلاك', required=True)
    journal_id = fields.Many2one('account.journal', required=True)

    date_to_first_week = fields.Date('إلى اولاسبوع')

    @api.multi
    def land_get_rested_ommat(self):
        last_scraped_f = 1.0
        last_rested_f = 1.0
        last_rested_m = 1.0
        for week in self.land_week_ids:
            # if week.l_catalogue_id:
            if week.l_code == 1:
                #  female اول سطر
                x = self.land_f_num
                # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
                week.l_scraped_ommat_f = x * week.l_scraped_f

                # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
                week.l_rested_ommat_f = x-week.l_scraped_ommat_f

                last_scraped_f = week.l_scraped_ommat_f
                last_rested_f = week.l_rested_ommat_f

                # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
                week.l_e_daily_feed_f = week.l_rested_ommat_f * week.l_daily_feed_f

                # اول سطرmale
                y = week.l_catalogue_id.land_m_num
                # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
                week.l_scraped_ommat_m = y * week.l_scraped_m

                # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
                week.l_rested_ommat_m = y-week.l_scraped_ommat_m

                last_scraped_m = week.l_scraped_ommat_m
                last_rested_m = week.l_rested_ommat_m


            else:
                # print('a5er kima llscrap =', last_scraped_f)
                week.l_scraped_ommat_f = last_rested_f * week.l_scraped_f

                last_scraped_f = week.l_scraped_ommat_f
                # print('a5er kima llscrap =', last_scraped_f)

                week.l_rested_ommat_f = last_rested_f-last_scraped_f

                last_rested_f = week.l_rested_ommat_f

                # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
                week.l_e_daily_feed_f = week.l_rested_ommat_f * week.l_daily_feed_f

                # print('a5er kima llscrap =', last_scraped_f)
                week.l_scraped_ommat_m = last_rested_m * week.l_scraped_m

                last_scraped_m = week.l_scraped_ommat_m
                # print('a5er kima llscrap =', last_scraped_f)

                week.l_rested_ommat_m = last_rested_m-last_scraped_m

                last_rested_m = week.l_rested_ommat_m
            week.l_total_weekly_production_m = week.l_total_weekly_production_f * week.l_rested_ommat_f
            week.l_evacuation_weekly_production_m = week.l_evacuation_weekly_production_f * week.l_rested_ommat_f
            week.l_hatching_m = week.l_hatching_f * week.l_rested_ommat_f

    @api.multi
    def land_ww_get_rested_ommat(self):
        last_scraped_f = 1.0
        last_rested_f = 1.0
        last_rested_m = 1.0
        for week in self.w_land_week_ids:
            # if week.l_catalogue_id:
            if week.l_code == 1:
                #  female اول سطر
                x = self.land_f_num
                # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
                week.l_scraped_ommat_f_ww = x * week.l_scraped_f_ww

                # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
                week.l_rested_ommat_f_ww = x-week.l_scraped_ommat_f_ww

                last_scraped_f = week.l_scraped_ommat_f_ww
                last_rested_f = week.l_rested_ommat_f_ww

                # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
                week.l_e_daily_feed_f_ww = week.l_rested_ommat_f_ww * week.l_daily_feed_f_ww

                # اول سطرmale
                y = week.l_catalogue_id_ww.land_m_num
                # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
                week.l_scraped_ommat_m_ww = y * week.l_scraped_m_ww

                # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
                week.l_rested_ommat_m_ww = y-week.l_scraped_ommat_m_ww

                last_scraped_m = week.l_scraped_ommat_m_ww
                last_rested_m = week.l_rested_ommat_m_ww


            else:
                # print('a5er kima llscrap =', last_scraped_f)
                week.l_scraped_ommat_f_ww = last_rested_f * week.l_scraped_f_ww

                last_scraped_f = week.l_scraped_ommat_f_ww
                # print('a5er kima llscrap =', last_scraped_f)

                week.l_rested_ommat_f_ww = last_rested_f-last_scraped_f

                last_rested_f = week.l_rested_ommat_f_ww

                # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
                week.l_e_daily_feed_f_ww = week.l_rested_ommat_f_ww * week.l_daily_feed_f_ww

                # print('a5er kima llscrap =', last_scraped_f)
                week.l_scraped_ommat_m_ww = last_rested_m * week.l_scraped_m_ww

                last_scraped_m = week.l_scraped_ommat_m_ww
                # print('a5er kima llscrap =', last_scraped_f)

                week.l_rested_ommat_m_ww = last_rested_m-last_scraped_m

                last_rested_m = week.l_rested_ommat_m_ww
            week.l_total_weekly_production_m_ww = week.l_total_weekly_production_f_ww * week.l_rested_ommat_f_ww
            week.l_evacuation_weekly_production_m_ww = week.l_evacuation_weekly_production_f_ww * week.l_rested_ommat_f_ww
            week.l_hatching_m = week.l_hatching_f_ww * week.l_rested_ommat_f_ww

    @api.multi
    def bat_get_rested_ommat(self):
        last_scraped_f = 1.0
        last_rested_f = 1.0
        last_rested_m = 1.0
        for week in self.bat_week_ids:
            # if week.l_catalogue_id:
            if week.b_code == 1:
                #  female اول سطر
                x = self.land_f_num
                # print('اول نافق = عدد الاناث * النسبه', x, week.b_scraped_f)
                week.b_scraped_ommat_f = x * week.b_scraped_f

                # print('اول باقى = عدد الاناث - نافق', x, week.b_scraped_ommat_f)
                week.b_rested_ommat_f = x-week.b_scraped_ommat_f

                last_scraped_f = week.b_scraped_ommat_f
                last_rested_f = week.b_rested_ommat_f

                # print('اول علف = الباقى - نسبة االعلف', x, week.b_scraped_ommat_f)
                week.b_e_daily_feed_f = week.b_rested_ommat_f * week.b_daily_feed_f

                # اول سطرmale
                y = week.b_catalogue_id.land_m_num
                # print('اول نافق = عدد الاناث * النسبه', x, week.b_scraped_f)
                week.b_scraped_ommat_m = y * week.b_scraped_m

                # print('اول باقى = عدد الاناث - نافق', x, week.b_scraped_ommat_f)
                week.b_rested_ommat_m = y-week.b_scraped_ommat_m

                last_scraped_m = week.b_scraped_ommat_m
                last_rested_m = week.b_rested_ommat_m


            else:
                # print('a5er kima llscrap =', last_scraped_f)
                week.b_scraped_ommat_f = last_rested_f * week.b_scraped_f

                last_scraped_f = week.b_scraped_ommat_f
                # print('a5er kima llscrap =', last_scraped_f)

                week.b_rested_ommat_f = last_rested_f-last_scraped_f

                last_rested_f = week.b_rested_ommat_f

                # print('اول علف = الباقى - نسبة االعلف', x, week.b_scraped_ommat_f)
                week.b_e_daily_feed_f = week.b_rested_ommat_f * week.b_daily_feed_f

                # print('a5er kima llscrap =', last_scraped_f)
                week.b_scraped_ommat_m = last_rested_m * week.b_scraped_m

                last_scraped_m = week.b_scraped_ommat_m
                # print('a5er kima llscrap =', last_scraped_f)

                week.b_rested_ommat_m = last_rested_m-last_scraped_m

                last_rested_m = week.b_rested_ommat_m
            week.b_total_weekly_production_m = week.b_total_weekly_production_f * week.b_rested_ommat_f
            week.b_evacuation_weekly_production_m = week.b_evacuation_weekly_production_f * week.b_rested_ommat_f
            week.b_hatching_m = week.b_hatching_f * week.b_rested_ommat_f

    @api.multi
    def bat_ww_get_rested_ommat(self):
        last_scraped_f = 1.0
        last_rested_f = 1.0
        last_rested_m = 1.0
        for week in self.w_bat_week_ids:
            # if week.l_catalogue_id:
            if week.b_code == 1:
                #  female اول سطر
                x = self.land_f_num
                # print('اول نافق = عدد الاناث * النسبه', x, week.b_scraped_f)
                week.b_scraped_ommat_f_ww = x * week.b_scraped_f_ww

                # print('اول باقى = عدد الاناث - نافق', x, week.b_scraped_ommat_f)
                week.b_rested_ommat_f_ww = x-week.b_scraped_ommat_f_ww

                last_scraped_f = week.b_scraped_ommat_f_ww
                last_rested_f = week.b_rested_ommat_f_ww

                # print('اول علف = الباقى - نسبة االعلف', x, week.b_scraped_ommat_f)
                week.b_e_daily_feed_f_ww = week.b_rested_ommat_f_ww * week.b_daily_feed_f_ww

                # اول سطرmale
                y = week.b_catalogue_id_ww.land_m_num
                # print('اول نافق = عدد الاناث * النسبه', x, week.b_scraped_f)
                week.b_scraped_ommat_m_ww = y * week.b_scraped_m_ww

                # print('اول باقى = عدد الاناث - نافق', x, week.b_scraped_ommat_f)
                week.b_rested_ommat_m_ww = y-week.b_scraped_ommat_m_ww

                last_scraped_m = week.b_scraped_ommat_m_ww
                last_rested_m = week.b_rested_ommat_m_ww


            else:
                # print('a5er kima llscrap =', last_scraped_f)
                week.b_scraped_ommat_f_ww = last_rested_f * week.b_scraped_f_ww

                last_scraped_f = week.b_scraped_ommat_f_ww
                # print('a5er kima llscrap =', last_scraped_f)

                week.b_rested_ommat_f_ww = last_rested_f-last_scraped_f

                last_rested_f = week.b_rested_ommat_f_ww

                # print('اول علف = الباقى - نسبة االعلف', x, week.b_scraped_ommat_f)
                week.b_e_daily_feed_f_ww = week.b_rested_ommat_f_ww * week.b_daily_feed_f_ww

                # print('a5er kima llscrap =', last_scraped_f)
                week.b_scraped_ommat_m_ww = last_rested_m * week.b_scraped_m_ww

                last_scraped_m = week.b_scraped_ommat_m_ww
                # print('a5er kima llscrap =', last_scraped_f)

                week.b_rested_ommat_m_ww = last_rested_m-last_scraped_m

                last_rested_m = week.b_rested_ommat_m_ww
            week.b_total_weekly_production_m_ww = week.b_total_weekly_production_f_ww * week.b_rested_ommat_f_ww
            week.b_evacuation_weekly_production_m_ww = week.b_evacuation_weekly_production_f_ww * week.b_rested_ommat_f_ww
            week.b_hatching_m = week.b_hatching_f_ww * week.b_rested_ommat_f_ww

    @api.multi
    @api.depends('bat_week_ids')
    def get_last_rested_b(self):
        for week in self.bat_week_ids:
            # TODO check this week.b_code == 3 week.b_code == len(self.bat_week_ids) and week.b_code >= 24
            if week.b_code == len(self.bat_week_ids):
                self.last_rested_ommat_fb = week.b_rested_ommat_f
                self.last_rested_ommat_mb = week.b_rested_ommat_m

    @api.multi
    @api.depends('land_week_ids')
    def get_last_rested_l(self):
        for rec in self:
            if rec.land_week_ids:
                for week in rec.land_week_ids:
                    print('in for')
                    # TODO check this week.l_code == len(self.land_week_ids) and week.l_code >= 3
                    if week.l_code == len(rec.land_week_ids):
                        print('in if')
                        if week.l_rested_ommat_f and week.l_rested_ommat_m:
                            print('l code', week.l_code)
                            print('week.id', week.id)
                            print('len', len(rec.land_week_ids))
                            print('week.l_rested_ommat_f', week.l_rested_ommat_f)
                            rec.last_rested_ommat_fl = week.l_rested_ommat_f
                            rec.last_rested_ommat_ml = week.l_rested_ommat_m
                            # break

    @api.multi
    @api.depends('last_rested_ommat_fl', 'weight_avg_l',
                 'kilo_price_l', 'last_rested_ommat_ml',
                 'last_rested_ommat_fb', 'weight_avg_b',
                 'kilo_price_b', 'last_rested_ommat_mb')
    def get_e_value(self):
        e_value_fl = self.last_rested_ommat_fl * self.weight_avg_l * self.kilo_price_l
        e_value_ml = self.last_rested_ommat_ml * self.weight_avg_l * self.kilo_price_l
        self.e_value_l = e_value_fl+e_value_ml

        e_value_fb = self.last_rested_ommat_fb * self.weight_avg_b * self.kilo_price_b
        e_value_mb = self.last_rested_ommat_mb * self.weight_avg_b * self.kilo_price_b

        self.e_value_b = e_value_fb+e_value_mb

    @api.multi
    @api.constrains('date_from', 'date_to_first_week')
    def check_dates(self):
        for rec in self:
            if rec.date_from >= rec.date_to_first_week:
                raise ValidationError('Please Edit Dates')

    @api.multi
    @api.constrains('flock_num', 'land_f_num', 'land_m_num', 'bat_f_num', 'bat_m_num')
    def check_numbers(self):
        for rec in self:
            if rec.land_f_num+rec.land_m_num+rec.bat_f_num+rec.bat_m_num > rec.flock_num:
                raise ValidationError('Please Edit Chicken  Numbers')

    @api.multi
    @api.constrains('weight_avg_l')
    def check_weight_avg_l(self):
        for rec in self:
            if rec.weight_avg_l <= 0.00:
                raise ValidationError('dddddddd Edit Dates')

    @api.multi
    def upload_weeks(self):
        if self.flock_id:
            land_week_line = []
            bat_week_line = []
            w_land_week_line = []
            w_bat_week_line = []
            last_wn_land_week = 0
            last_wn_bat_week_line = 0
            last_wn_w_land_week_line = 0
            last_wn_w_bat_week_line = 0
            init_no_l = 1
            init_no_b = 1
            init_no_lw = 1
            init_no_bw = 1
            for week in self.flock_id.land_week_ids:
                print(week.l_code)
                week.l_code = init_no_l
                init_no_l = init_no_l+1

            for week in self.flock_id.bat_week_ids:
                print(week.b_code)
                week.b_code = init_no_b
                init_no_b = init_no_b+1

            for week in self.flock_id.w_land_week_ids:
                print(week.l_code)
                week.l_code = init_no_lw
                init_no_lw = init_no_lw+1

            for week in self.flock_id.w_bat_week_ids:
                print(week.b_code)
                week.b_code = init_no_bw
                init_no_bw = init_no_bw+1

            if self.land_week_ids:

                for check_line in self.land_week_ids:
                    if last_wn_land_week < check_line.l_code:
                        last_wn_land_week = check_line.l_code
                        l_date_from = check_line.l_date_from
                        l_date_to = check_line.l_date_to
            else:
                l_date_from = str(self.date_from)
                l_date_to = str(self.date_to_first_week)
            check = False
            for line in self.flock_id.land_week_ids:
                if line.l_code > last_wn_land_week:

                    if last_wn_land_week != 0:
                        l_date_from = l_date_to+relativedelta(days=1)
                        l_date_to = l_date_from+relativedelta(days=7)

                    elif check == True:
                        l_date_from = fields.Datetime.from_string(l_date_to)+relativedelta(days=1)
                        l_date_to = fields.Datetime.from_string(l_date_from)+relativedelta(days=7)

                    land_week_line.append((0, 0, {
                        'l_code': line.l_code,
                        # 'l_catalogue_id': self.id,
                        # 'l_flock_id': line.l_flock_id.id,
                        'l_date_from': l_date_from,
                        'l_date_to': l_date_to,
                        'l_total_age': line.l_total_age,
                        'l_productive_age': line.l_productive_age,
                        'l_scraped_f': line.l_scraped_f,
                        'l_scraped_m': line.l_scraped_m,
                        'l_daily_feed_f': line.l_daily_feed_f,
                        'l_daily_feed_m': line.l_daily_feed_m,
                        'l_total_weekly_production_f': line.l_total_weekly_production_f,
                        'l_evacuation_weekly_production_f': line.l_evacuation_weekly_production_f,
                        'l_hatching_f': line.l_hatching_f,
                    }))
                    check = True

            if self.bat_week_ids:
                for check_line in self.bat_week_ids:
                    if last_wn_bat_week_line < check_line.b_code:
                        last_wn_bat_week_line = check_line.b_code
                        b_date_from = check_line.b_date_from
                        b_date_to = check_line.b_date_to
            else:
                b_date_from = str(self.date_from)
                b_date_to = str(self.date_to_first_week)
            check = False
            for line in self.flock_id.bat_week_ids:
                if line.b_code > last_wn_bat_week_line:
                    if last_wn_bat_week_line != 0:
                        b_date_from = b_date_to+relativedelta(days=1)
                        b_date_to = b_date_from+relativedelta(days=7)

                    elif check == True:
                        b_date_from = fields.Datetime.from_string(b_date_to)+relativedelta(days=1)
                        b_date_to = fields.Datetime.from_string(b_date_from)+relativedelta(days=7)

                    bat_week_line.append((0, 0, {
                        'b_code': line.b_code,
                        'b_date_from': b_date_from,
                        'b_date_to': b_date_to,
                        'b_total_age': line.b_total_age,
                        'b_productive_age': line.b_productive_age,
                        'b_scraped_f': line.b_scraped_f,
                        'b_scraped_m': line.b_scraped_m,
                        'b_daily_feed_f': line.b_daily_feed_f,
                        'b_daily_feed_m': line.b_daily_feed_m,
                        'b_total_weekly_production_f': line.b_total_weekly_production_f,
                        'b_evacuation_weekly_production_f': line.b_evacuation_weekly_production_f,
                        'b_hatching_f': line.b_hatching_f,
                    }))
                    check = True

            if self.w_land_week_ids:
                for check_line in self.w_land_week_ids:
                    if last_wn_w_land_week_line < check_line.l_code:
                        last_wn_w_land_week_line = check_line.l_code

            for line in self.flock_id.w_land_week_ids:
                if line.l_code > last_wn_w_land_week_line:
                    w_land_week_line.append((0, 0, {
                        'l_code': line.l_code,
                        'l_total_age_ww': line.l_total_age_ww,
                        'l_productive_age_ww': line.l_productive_age_ww,
                        'l_scraped_f_ww': line.l_scraped_f_ww,
                        'l_scraped_m_ww': line.l_scraped_m_ww,
                        'l_daily_feed_f_ww': line.l_daily_feed_f_ww,
                        'l_daily_feed_m_ww': line.l_daily_feed_m_ww,
                        'l_total_weekly_production_f_ww': line.l_total_weekly_production_f_ww,
                        'l_evacuation_weekly_production_f_ww': line.l_evacuation_weekly_production_f_ww,
                        # 'l_catalogue_id': self.id,
                        'l_hatching_f_ww': line.l_hatching_f_ww,
                    }))

            if self.w_bat_week_ids:
                for check_line in self.w_bat_week_ids:
                    if last_wn_w_bat_week_line < check_line.b_co22de:
                        last_wn_w_bat_week_line = check_line.b_code

            for line in self.flock_id.w_bat_week_ids:
                if line.b_code > last_wn_land_week:
                    w_bat_week_line.append((0, 0, {
                        'b_code': line.b_code,
                        'b_total_age_ww': line.b_total_age_ww,
                        'b_productive_age_ww': line.b_productive_age_ww,
                        'b_scraped_f_ww': line.b_scraped_f_ww,
                        'b_scraped_m_ww': line.b_scraped_m_ww,
                        'b_daily_feed_f_ww': line.b_daily_feed_f_ww,
                        'b_daily_feed_m_ww': line.b_daily_feed_m_ww,
                        'b_total_weekly_production_f_ww': line.b_total_weekly_production_f_ww,
                        'b_evacuation_weekly_production_f_ww': line.b_evacuation_weekly_production_f_ww,
                        'b_hatching_f_ww': line.b_hatching_f_ww,
                    }))

            self.update({'land_week_ids': land_week_line,
                         'bat_week_ids': bat_week_line,
                         'w_land_week_ids': w_land_week_line,
                         'w_bat_week_ids': w_bat_week_line
                         })

            self.land_get_rested_ommat()
            self.land_ww_get_rested_ommat()
            self.bat_get_rested_ommat()
            self.bat_ww_get_rested_ommat()

    # @api.multi
    # def unlink(self):
    #     result = super(ommat_catalogue, self).unlink()
    #     if self.land_week_ids:
    #         for line in self.land_week_ids:
    #             line.unlink()
    #     # if self.bat_week_ids:
    #     #     self.bat_week_ids.unlink()
    #     # if self.w_land_week_ids:
    #     #     self.w_land_week_ids.unlink()
    #     # if self.w_bat_week_ids:
    #     #     self.w_bat_week_ids.unlink()
    #     return result
