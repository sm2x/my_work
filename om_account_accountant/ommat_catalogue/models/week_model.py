# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LandWeek(models.Model):
    _name = 'land.week'
    _description = "Land Week"
    _rec_name = 'l_catalogue_id'

    l_catalogue_id = fields.Many2one('ommat.catalogue', string="الكتالوج")
    l_flock_id = fields.Many2one('flock.model', string="القطيع")

    l_code = fields.Integer('الأسبوع')
    l_code_c = fields.Integer('الأسبوع للقطيع', store=True)

    l_date_from = fields.Datetime('من')
    l_date_to = fields.Datetime('إلى')

    l_total_age = fields.Integer('العمر الكلى')
    l_productive_age = fields.Integer('العمر الانتاجى')

    l_scraped_f = fields.Float('النافق والفرزه -انثى', digits=(16, 4))
    l_scraped_m = fields.Float('النافق والفرزه -ذكر', digits=(16, 4))

    l_scraped_ommat_f = fields.Float('عدد الامهات النافقه -انثى', digits=(16, 4))
    l_scraped_ommat_m = fields.Float('عدد الامهات النافقه -ذكر', digits=(16, 4))

    l_actual_ommat_f = fields.Float('عدد النافق الفعلى -انثى', compute='all_real_land_no', digits=(16, 4))
    l_actual_ommat_m = fields.Float('عدد النافق الفعلى -ذكر', compute='all_real_land_no', digits=(16, 4))

    l_rested_ommat_f = fields.Float(string='عدد الامهات الباقيه -انثى',
                                    digits=(16, 4))
    l_rested_ommat_m = fields.Float('عدد الامهات الباقيه -ذكر', digits=(16, 4))

    l_daily_feed_f = fields.Float('العلف اليومى -أنثى', digits=(16, 4))
    l_daily_feed_m = fields.Float('العلف اليومى -ذكر', digits=(16, 4))

    l_actual_daily_feed_f = fields.Float('العلف الفعلى اليومى -أنثى', compute='all_real_land_no', digits=(16, 4))
    l_actual_daily_feed_m = fields.Float('العلف الفعلى اليومى -ذكر', compute='all_real_land_no', digits=(16, 4))

    l_e_daily_feed_f = fields.Float('العلف اليومى محسوب -أنثى', digits=(16, 4))
    l_e_daily_feed_m = fields.Float('العلف اليومى محسوب -ذكر', digits=(16, 4))

    l_total_weekly_production_f = fields.Float('الانتاج الكلى الاسبوعى ', digits=(16, 4))

    l_total_weekly_production_m = fields.Float('الكلى الاسبوعى القياسى',
                                               digits=(16, 4))
    l_total_weekly_production_pro = fields.Float('الكلى الاسبوعى الفعلى', compute='all_real_land_no', digits=(16, 4))

    l_evacuation_weekly_production_f = fields.Float('الانتاج التفريغ الاسبوعى ', digits=(16, 4))

    l_evacuation_weekly_production_m = fields.Float('التفريغ الاسبوعى القياسى',
                                                    digits=(16, 4))

    l_evacuation_weekly_production_lab = fields.Float('التفريغ الاسبوعى الفعلى', compute='all_real_land_no',
                                                      digits=(16, 4))

    l_hatching_f = fields.Float('الفقس ', digits=(16, 4))

    l_hatching_m = fields.Float('الفقس الكلى', digits=(16, 4))

    @api.multi
    @api.depends('l_code')
    def all_real_land_no(self):

        scrap_products = self.env['product.product'].search([('scrap', '=', True)])
        feed_products = self.env['product.product'].search([('feed_type', '=', 'feed')])

        for rec in self:
            female_scrap_r_total = 0.0000
            feed_female_r_total = 0.0000
            male_scrap_r_total = 0.0000
            feed_male_r_total = 0.0000

            mo_farming_female = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                                  ('farming', '=', True),

                                                                  ('dynasty', '=', rec.l_catalogue_id.dynasty.id),
                                                                  ('week_no', '=', rec.l_code),
                                                                  ('type_l_b', '=', 'land')])

            if mo_farming_female:
                for mo in mo_farming_female:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                        for mat in mo.move_raw_ids:
                            if mat.product_id.id in feed_products.ids:
                                feed_female_r_total = feed_female_r_total+mat.quantity_done
                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

                        for mat in mo.move_raw_ids:
                            if mat.product_id.id in feed_products.ids:
                                feed_male_r_total = feed_male_r_total+mat.quantity_done

            production_r_total = 0.000

            mo_production_total = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                                    ('pro', '=', True),

                                                                    ('dynasty', '=', rec.l_catalogue_id.dynasty.id),
                                                                    ('week_no', '=', rec.l_code),
                                                                    ('type_l_b', '=', 'land')])

            if mo_production_total:
                for mo in mo_production_total:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                production_r_total = production_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                production_r_total = production_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

            evac_r_total = 0.000
            mo_evac_total = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                              ('lab', '=', True),

                                                              ('dynasty', '=', rec.l_catalogue_id.dynasty.id),
                                                              ('week_no', '=', rec.l_code),
                                                              ('type_l_b', '=', 'land')])

            if mo_evac_total:
                for mo in mo_evac_total:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                evac_r_total = evac_r_total+finish.qty_done


                            elif finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                evac_r_total = evac_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

            rec.l_actual_ommat_f = female_scrap_r_total
            rec.l_actual_ommat_m = male_scrap_r_total
            rec.l_actual_daily_feed_f = feed_female_r_total
            rec.l_actual_daily_feed_m = feed_male_r_total
            rec.l_total_weekly_production_pro = production_r_total
            rec.l_evacuation_weekly_production_lab = evac_r_total

    # @api.multi
    # def land_calculate_week_no(self):
    #     init_no = 1
    #     for week in self:
    #         # print('week.l_code =', week.l_code)
    #         week.l_code_c = init_no
    #         init_no = init_no+1

    # @api.multi
    # @api.depends('l_catalogue_id')
    # def land_get_rested_ommat_f(self):
    #
    #     last_scraped_f = 1.0
    #     last_rested_f = 1.0
    #     for week in self:
    #         if week.l_catalogue_id:
    #             if week.l_code == 1:
    #                 # اول سطر
    #                 x = week.l_catalogue_id.land_f_num
    #                 # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
    #                 week.l_scraped_ommat_f = x * week.l_scraped_f
    #
    #                 # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
    #                 week.l_rested_ommat_f = x-week.l_scraped_ommat_f
    #
    #                 last_scraped_f = week.l_scraped_ommat_f
    #                 last_rested_f = week.l_rested_ommat_f
    #
    #                 # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
    #                 week.l_e_daily_feed_f = week.l_rested_ommat_f * week.l_daily_feed_f
    #
    #             else:
    #                 # print('a5er kima llscrap =', last_scraped_f)
    #                 week.l_scraped_ommat_f = last_rested_f * week.l_scraped_f
    #
    #                 last_scraped_f = week.l_scraped_ommat_f
    #                 # print('a5er kima llscrap =', last_scraped_f)
    #
    #                 week.l_rested_ommat_f = last_rested_f-last_scraped_f
    #
    #                 last_rested_f = week.l_rested_ommat_f
    #
    #                 # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
    #                 week.l_e_daily_feed_f = week.l_rested_ommat_f * week.l_daily_feed_f

    # @api.multi
    # @api.depends('l_catalogue_id')
    # def land_get_rested_ommat_m(self):
    #     last_scraped_m = 1.0
    #     last_rested_m = 1.0
    #     for week in self:
    #         if week.l_catalogue_id:
    #             # y = 1.0
    #             if week.l_code == 1:
    #                 # اول سطر
    #                 x = week.l_catalogue_id.land_m_num
    #                 # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
    #                 week.l_scraped_ommat_m = x * week.l_scraped_m
    #
    #                 # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
    #                 week.l_rested_ommat_m = x-week.l_scraped_ommat_m
    #
    #                 last_scraped_m = week.l_scraped_ommat_m
    #                 last_rested_m = week.l_rested_ommat_m
    #
    #             else:
    #                 # print('a5er kima llscrap =', last_scraped_f)
    #                 week.l_scraped_ommat_m = last_rested_m * week.l_scraped_m
    #
    #                 last_scraped_m = week.l_scraped_ommat_m
    #                 # print('a5er kima llscrap =', last_scraped_f)
    #
    #                 week.l_rested_ommat_m = last_rested_m-last_scraped_m
    #
    #                 last_rested_m = week.l_rested_ommat_m


class WLandWeek(models.Model):
    _name = 'land.week.w'
    _description = "Land Week"
    l_code = fields.Integer('الأسبوع')
    l_code_cww = fields.Integer('الأسبوع للقطيع', store=True)

    l_catalogue_id_ww = fields.Many2one('ommat.catalogue', string="الكتالوج")
    l_flock_id_ww = fields.Many2one('flock.model', string="القطيع")

    l_date_from_ww = fields.Datetime('من')
    l_date_to_ww = fields.Datetime('إلى')

    l_total_age_ww = fields.Integer('العمر الكلى')
    l_productive_age_ww = fields.Integer('العمر الانتاجى')

    l_scraped_f_ww = fields.Float('النافق والفرزه -انثى', digits=(16, 4))
    l_scraped_m_ww = fields.Float('النافق والفرزه -ذكر', digits=(16, 4))

    l_scraped_ommat_f_ww = fields.Float('عدد الامهات النافقه -انثى', digits=(16, 4))
    l_scraped_ommat_m_ww = fields.Float('عدد الامهات النافقه -ذكر', digits=(16, 4))

    l_actual_ommat_f_ww = fields.Float('عدد النافق الفعلى -انثى', compute='all_real_land_no', digits=(16, 4))
    l_actual_ommat_m_ww = fields.Float('عدد النافق الفعلى -ذكر', compute='all_real_land_no', digits=(16, 4))

    l_rested_ommat_f_ww = fields.Float(string='عدد الامهات الباقيه -انثى',
                                       digits=(16, 4))
    l_rested_ommat_m_ww = fields.Float('عدد الامهات الباقيه -ذكر',digits=(16, 4))

    l_daily_feed_f_ww = fields.Float('العلف اليومى -أنثى', digits=(16, 4))
    l_daily_feed_m_ww = fields.Float('العلف اليومى -ذكر', digits=(16, 4))

    l_actual_daily_feed_f_ww = fields.Float('العلف الفعلى اليومى -أنثى', compute='all_real_land_no', digits=(16, 4))
    l_actual_daily_feed_m_ww = fields.Float('العلف الفعلى اليومى -ذكر', compute='all_real_land_no', digits=(16, 4))

    l_e_daily_feed_f_ww = fields.Float('العلف اليومى محسوب -أنثى', compute='all_real_land_no', digits=(16, 4))
    l_e_daily_feed_m_ww = fields.Float('العلف اليومى محسوب -ذكر', compute='all_real_land_no', digits=(16, 4))

    l_total_weekly_production_f_ww = fields.Float('الانتاج الكلى الاسبوعى ', digits=(16, 4))

    l_total_weekly_production_m_ww = fields.Float('الكلى الاسبوعى القياسى', compute='all_real_land_no',
                                                  digits=(16, 4))
    l_total_weekly_production_pro_ww = fields.Float('الكلى الاسبوعى الفعلى', compute='all_real_land_no',
                                                    digits=(16, 4))

    l_evacuation_weekly_production_f_ww = fields.Float('الانتاج التفريغ الاسبوعى ', digits=(16, 4))

    l_evacuation_weekly_production_m_ww = fields.Float('التفريغ الاسبوعى القياسى',
                                                       digits=(16, 4))
    l_evacuation_weekly_production_lab_ww = fields.Float('التفريغ الاسبوعى الفعلى', compute='all_real_land_no',
                                                         digits=(16, 4))

    l_hatching_f_ww = fields.Float('الفقس ', digits=(16, 4))

    l_hatching_m_ww = fields.Float('الفقس الكلى',digits=(16, 4))

    # @api.multi
    # def land_calculate_week_no(self):
    #     init_no = 1
    #     for week in self:
    #         # print('week.l_code =', week.l_code)
    #         week.l_code_cww = init_no
    #         init_no = init_no+1

    @api.multi
    @api.depends('l_code')
    def all_real_land_no(self):

        scrap_products = self.env['product.product'].search([('scrap', '=', True)])
        feed_products = self.env['product.product'].search([('feed_type', '=', 'feed')])

        for rec in self:
            female_scrap_r_total = 0.0000
            feed_female_r_total = 0.0000
            male_scrap_r_total = 0.0000
            feed_male_r_total = 0.0000

            mo_farming_female = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                                  ('farming', '=', True),

                                                                  ('dynasty', '=', rec.l_catalogue_id_ww.dynasty.id),
                                                                  ('week_no', '=', rec.l_code),
                                                                  ('type_l_b', '=', 'land')])

            if mo_farming_female:
                for mo in mo_farming_female:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                        for mat in mo.move_raw_ids:
                            if mat.product_id.id in feed_products.ids:
                                feed_female_r_total = feed_female_r_total+mat.quantity_done
                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

                        for mat in mo.move_raw_ids:
                            if mat.product_id.id in feed_products.ids:
                                feed_male_r_total = feed_male_r_total+mat.quantity_done

            production_r_total = 0.000

            mo_production_total = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                                    ('pro', '=', True),

                                                                    ('dynasty', '=', rec.l_catalogue_id_ww.dynasty.id),
                                                                    ('week_no', '=', rec.l_code),
                                                                    ('type_l_b', '=', 'land')])

            if mo_production_total:
                for mo in mo_production_total:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                production_r_total = production_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                production_r_total = production_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

            evac_r_total = 0.000
            mo_evac_total = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                              ('lab', '=', True),

                                                              ('dynasty', '=', rec.l_catalogue_id_ww.dynasty.id),
                                                              ('week_no', '=', rec.l_code),
                                                              ('type_l_b', '=', 'land')])

            if mo_evac_total:
                for mo in mo_evac_total:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                evac_r_total = evac_r_total+finish.qty_done


                            elif finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                evac_r_total = evac_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

            rec.l_actual_ommat_f_ww = female_scrap_r_total
            rec.l_actual_ommat_m_ww = male_scrap_r_total
            rec.l_actual_daily_feed_f_ww = feed_female_r_total
            rec.l_actual_daily_feed_m_ww = feed_male_r_total
            rec.l_total_weekly_production_pro_ww = production_r_total
            rec.l_evacuation_weekly_production_lab_ww = evac_r_total

    # @api.multi
    # @api.depends('l_catalogue_id_ww')
    # def land_get_rested_ommat_f(self):
    #     last_scraped_f = 1.0
    #     last_rested_f = 1.0
    #     for week in self:
    #         # y = 1.0
    #         if week.l_code == 1:
    #             # اول سطر
    #             x = week.l_catalogue_id_ww.land_f_num
    #             # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
    #             week.l_scraped_ommat_f_ww = x * week.l_scraped_f_ww
    #
    #             # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
    #             week.l_rested_ommat_f_ww = x-week.l_scraped_ommat_f_ww
    #
    #             last_scraped_f = week.l_scraped_ommat_f_ww
    #             last_rested_f = week.l_rested_ommat_f_ww
    #
    #             # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
    #             week.l_e_daily_feed_f_ww = week.l_rested_ommat_f_ww * week.l_daily_feed_f_ww
    #
    #         else:
    #             # print('a5er kima llscrap =', last_scraped_f)
    #             week.l_scraped_ommat_f_ww = last_rested_f * week.l_scraped_f_ww
    #
    #             last_scraped_f = week.l_scraped_ommat_f_ww
    #             # print('a5er kima llscrap =', last_scraped_f)
    #
    #             week.l_rested_ommat_f_ww = last_rested_f-last_scraped_f
    #
    #             last_rested_f = week.l_rested_ommat_f_ww
    #
    #             # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
    #             week.l_e_daily_feed_f_ww = week.l_rested_ommat_f_ww * week.l_daily_feed_f_ww
    #
    # @api.multi
    # @api.depends('l_catalogue_id_ww')
    # def land_get_rested_ommat_m(self):
    #     last_scraped_m = 1.0
    #     last_rested_m = 1.0
    #     for week in self:
    #         # y = 1.0
    #         if week.l_code == 1:
    #             # اول سطر
    #             x = week.l_catalogue_id_ww.land_m_num
    #             # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
    #             week.l_scraped_ommat_m_ww = x * week.l_scraped_m_ww
    #
    #             # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
    #             week.l_rested_ommat_m_ww = x-week.l_scraped_ommat_m_ww
    #
    #             last_scraped_m = week.l_scraped_ommat_m_ww
    #             last_rested_m = week.l_rested_ommat_m_ww
    #
    #         else:
    #             # print('a5er kima llscrap =', last_scraped_f)
    #             week.l_scraped_ommat_m_ww = last_rested_m * week.l_scraped_m_ww
    #
    #             last_scraped_m = week.l_scraped_ommat_m_ww
    #             # print('a5er kima llscrap =', last_scraped_f)
    #
    #             week.l_rested_ommat_m_ww = last_rested_m-last_scraped_m
    #
    #             last_rested_m = week.l_rested_ommat_m_ww


class BatteryWeek(models.Model):
    _name = 'bat.week'
    _description = "Battery Week"
    _rec_name = 'b_catalogue_id'

    b_catalogue_id = fields.Many2one('ommat.catalogue', string="الكتالوج")
    b_flock_id = fields.Many2one('flock.model', string="القطيع")

    b_code = fields.Integer('الأسبوع')
    b_code_c = fields.Integer('الأسبوع للقطيع', store=True)

    b_actual_ommat_f = fields.Float('عدد النافق الفعلى -انثى', compute='all_real_bat_no', digits=(16, 4))
    b_actual_ommat_m = fields.Float('عدد النافق الفعلى -ذكر', compute='all_real_bat_no', digits=(16, 4))
    b_actual_daily_feed_f = fields.Float('العلف الفعلى اليومى -أنثى', compute='all_real_bat_no', digits=(16, 4))
    b_actual_daily_feed_m = fields.Float('العلف الفعلى اليومى -ذكر', compute='all_real_bat_no', digits=(16, 4))
    b_total_weekly_production_pro = fields.Float('الكلى الاسبوعى الفعلى', compute='all_real_bat_no', digits=(16, 4))
    b_evacuation_weekly_production_lab = fields.Float('التفريغ الاسبوعى الفعلى', compute='all_real_bat_no',
                                                      digits=(16, 4))

    b_date_from = fields.Datetime('من')
    b_date_to = fields.Datetime('إلى')

    b_total_age = fields.Integer('العمر الكلى')
    b_productive_age = fields.Integer('العمر الانتاجى')

    b_scraped_f = fields.Float('النافق و الفرزه -انثى', digits=(16, 4))
    b_scraped_m = fields.Float('النافق و الفرزه -ذكر', digits=(16, 4))

    b_scraped_ommat_f = fields.Float('عدد الامهات النافقه -انثى', digits=(16, 4))
    b_scraped_ommat_m = fields.Float('عدد الامهات النافقه -ذكر', digits=(16, 4))

    b_rested_ommat_f = fields.Float('عدد الامهات الباقيه -انثى', digits=(16, 4))
    b_rested_ommat_m = fields.Float('عدد الامهات الباقيه -ذكر', digits=(16, 4))

    b_daily_feed_f = fields.Float('جم العلف  -أنثى', digits=(16, 4))
    b_daily_feed_m = fields.Float('جم العلف  -ذكر', digits=(16, 4))

    b_e_daily_feed_f = fields.Float('العلف اليومى -أنثى', digits=(16, 4))
    b_e_daily_feed_m = fields.Float('العلف اليومى -ذكر', digits=(16, 4))

    b_total_weekly_production_f = fields.Float('الانتاج الكلى الاسبوعى ', digits=(16, 4))

    b_total_weekly_production_m = fields.Float('الكلى الاسبوعى القياسى',
                                               digits=(16, 4))

    b_evacuation_weekly_production_f = fields.Float('الانتاج التفريغ الاسبوعى ', digits=(16, 4))

    b_evacuation_weekly_production_m = fields.Float('التفريغ الاسبوعى القياسى',
                                                    digits=(16, 4))

    b_hatching_f = fields.Float('نسبة الفقس ', digits=(16, 4))

    b_hatching_m = fields.Float('الفقس ', digits=(16, 4))

    @api.multi
    @api.depends('b_code')
    def all_real_bat_no(self):

        scrap_products = self.env['product.product'].search([('scrap', '=', True)])
        feed_products = self.env['product.product'].search([('feed_type', '=', 'feed')])

        for rec in self:
            female_scrap_r_total = 0.0000
            feed_female_r_total = 0.0000
            male_scrap_r_total = 0.0000
            feed_male_r_total = 0.0000

            mo_farming_female = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                                  ('farming', '=', True),

                                                                  ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
                                                                  ('week_no', '=', rec.b_code),
                                                                  ('type_l_b', '=', 'bat')])

            if mo_farming_female:
                for mo in mo_farming_female:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                        for mat in mo.move_raw_ids:
                            if mat.product_id.id in feed_products.ids:
                                feed_female_r_total = feed_female_r_total+mat.quantity_done
                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

                        for mat in mo.move_raw_ids:
                            if mat.product_id.id in feed_products.ids:
                                feed_male_r_total = feed_male_r_total+mat.quantity_done

            production_r_total = 0.000

            mo_production_total = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                                    ('pro', '=', True),

                                                                    ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
                                                                    ('week_no', '=', rec.b_code),
                                                                    ('type_l_b', '=', 'bat')])

            if mo_production_total:
                for mo in mo_production_total:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                production_r_total = production_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                production_r_total = production_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

            evac_r_total = 0.000
            mo_evac_total = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                              ('lab', '=', True),

                                                              ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
                                                              ('week_no', '=', rec.b_code),
                                                              ('type_l_b', '=', 'bat')])

            if mo_evac_total:
                for mo in mo_evac_total:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                evac_r_total = evac_r_total+finish.qty_done


                            elif finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                evac_r_total = evac_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

            rec.b_actual_ommat_f = female_scrap_r_total
            rec.b_actual_ommat_m = male_scrap_r_total
            rec.b_actual_daily_feed_f = feed_female_r_total
            rec.b_actual_daily_feed_m = feed_male_r_total
            rec.b_total_weekly_production_pro = production_r_total
            rec.b_evacuation_weekly_production_lab = evac_r_total

    # @api.multi
    # def bat_calculate_week_no(self):
    #     init_no = 1
    #     for week in self:
    #         # print('week.l_code =', week.l_code)
    #         week.b_code_c = init_no
    #         init_no = init_no+1

    # @api.multi
    # @api.depends('b_catalogue_id')
    # def bat_get_rested_ommat_f(self):
    #     last_scraped_f = 1.0
    #     last_rested_f = 1.0
    #     for week in self:
    #         # y = 1.0
    #         if week.b_code == 1:
    #             # اول سطر
    #             x = week.b_catalogue_id.bat_f_num
    #             # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
    #             week.b_scraped_ommat_f = x * week.b_scraped_f
    #
    #             # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
    #             week.b_rested_ommat_f = x-week.b_scraped_ommat_f
    #
    #             last_scraped_f = week.b_scraped_ommat_f
    #             last_rested_f = week.b_rested_ommat_f
    #
    #             # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
    #             week.b_e_daily_feed_f = week.b_rested_ommat_f * week.b_daily_feed_f
    #
    #         else:
    #             # print('a5er kima llscrap =', last_scraped_f)
    #             week.b_scraped_ommat_f = last_rested_f * week.b_scraped_f
    #
    #             last_scraped_f = week.b_scraped_ommat_f
    #             # print('a5er kima llscrap =', last_scraped_f)
    #
    #             week.b_rested_ommat_f = last_rested_f-last_scraped_f
    #
    #             last_rested_f = week.b_rested_ommat_f
    #
    #             # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
    #             week.b_e_daily_feed_f = week.b_rested_ommat_f * week.b_daily_feed_f
    #
    # @api.multi
    # @api.depends('b_catalogue_id')
    # def bat_get_rested_ommat_m(self):
    #     last_scraped_m = 1.0
    #     last_rested_m = 1.0
    #     for week in self:
    #         # y = 1.0
    #         if week.b_code == 1:
    #             # اول سطر
    #             x = week.b_catalogue_id.bat_m_num
    #             # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
    #             week.b_scraped_ommat_m = x * week.b_scraped_m
    #
    #             # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
    #             week.b_rested_ommat_m = x-week.b_scraped_ommat_m
    #
    #             last_scraped_m = week.b_scraped_ommat_m
    #             last_rested_m = week.b_rested_ommat_m
    #
    #         else:
    #             # print('a5er kima llscrap =', last_scraped_f)
    #             week.b_scraped_ommat_m = last_rested_m * week.b_scraped_m
    #
    #             last_scraped_m = week.b_scraped_ommat_m
    #             # print('a5er kima llscrap =', last_scraped_f)
    #
    #             week.b_rested_ommat_m = last_rested_m-last_scraped_m
    #
    #             last_rested_m = week.b_rested_ommat_m

    # @api.multi
    # @api.depends('b_total_weekly_production_f', 'b_catalogue_id', 'b_code',
    #              'b_rested_ommat_f', 'b_evacuation_weekly_production_f', 'b_hatching_f')
    # def b_get_weekly_production(self):
    #     for rec in self:
    #         rec.b_total_weekly_production_m = rec.b_total_weekly_production_f * rec.b_rested_ommat_f
    #         rec.b_evacuation_weekly_production_m = rec.b_evacuation_weekly_production_f * rec.b_rested_ommat_f
    #         rec.b_hatching_m = rec.b_hatching_f * rec.b_rested_ommat_f
    #
    #         mo_fbb_obj = rec.env['mrp.production'].search([('state', '=', "done"),
    #                                                        ('bom_id.pro', '=', True),
    #                                                        ('bom_id.gender', '=', "female"),
    #                                                        ('bom_id.dynasty', '=', rec.b_catalogue_id.dynasty.id),
    #                                                        ('bom_id.week_no', '=', rec.b_code),
    #                                                        ('bom_id.dest_lb_type', '=', 'bat')])
    #
    #         if mo_fbb_obj:
    #             qty_fl = 0
    #             for mo in mo_fbb_obj:
    #                 # print('inner')
    #                 # print(mo.id)
    #                 # print(mo.state)
    #                 qty_fl = qty_fl+mo.product_qty
    #             rec.b_total_weekly_production_pro = qty_fl
    #
    #         mo_fbl_obj = rec.env['mrp.production'].search([('state', '=', "done"),
    #                                                        ('bom_id.lab', '=', True),
    #                                                        ('bom_id.gender', '=', "female"),
    #                                                        ('bom_id.dynasty', '=', rec.b_catalogue_id.dynasty.id),
    #                                                        ('bom_id.week_no', '=', rec.b_code),
    #                                                        ('bom_id.dest_lb_type', '=', 'bat')])
    #
    #         if mo_fbl_obj:
    #             qty_fl = 0
    #             for mo in mo_fbl_obj:
    #                 # print('inner')
    #                 # print(mo.id)
    #                 # print(mo.state)
    #                 qty_fl = qty_fl+mo.product_qty
    #             rec.b_evacuation_weekly_production_lab = qty_fl
    #
    # @api.multi
    # @api.depends('b_catalogue_id', 'b_code')
    # def bat_actual_daily_feed(self):
    #     for rec in self:
    #         f_move_lines = rec.env['stock.move'].search([('mrp_state', '=', "done"),
    #                                                      ('gender', '=', "female"),
    #                                                      ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
    #                                                      ('week_no', '=', rec.b_code),
    #                                                      ('loc_type', '=', 'bat'),
    #                                                      ('product_id.feed_type', '=', 'feed')])
    #         m_move_lines = rec.env['stock.move'].search([('mrp_state', '=', "done"),
    #                                                      ('gender', '=', "male"),
    #                                                      ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
    #                                                      ('week_no', '=', rec.b_code),
    #                                                      ('loc_type', '=', 'bat'),
    #                                                      ('product_id.feed_type', '=', 'feed')])
    #
    #         f_qty = 0
    #         m_qty = 0
    #         # print(len(f_move_lines))
    #         # print(len(m_move_lines))
    #
    #         if m_move_lines or f_move_lines:
    #             for raw_line in f_move_lines:
    #                 print('mrp_state', raw_line.mrp_state)
    #                 f_qty = f_qty+raw_line.quantity_done
    #
    #             rec.b_actual_daily_feed_f = f_qty
    #             # print(f_qty)
    #
    #             for raw_line in m_move_lines:
    #                 m_qty = m_qty+raw_line.quantity_done
    #
    #             rec.b_actual_daily_feed_m = m_qty
    #
    # @api.multi
    # @api.depends('b_catalogue_id', 'b_code')
    # def bat_actual_ommat(self):
    #     for rec in self:
    #         by_product_fb_obj = rec.env['stock.move.line'].search([('mrp_state', '=', "done"),
    #                                                                ('product_id.scrap', '=', True),
    #                                                                ('gender', '=', "female"),
    #                                                                ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
    #                                                                ('week_no', '=', rec.b_code),
    #                                                                ('loc_type', '=', 'bat')])
    #
    #         by_product_mb_obj = rec.env['stock.move.line'].search([('mrp_state', '=', "done"),
    #                                                                ('product_id.scrap', '=', True),
    #                                                                ('gender', '=', "male"),
    #                                                                ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
    #                                                                ('week_no', '=', rec.b_code),
    #                                                                ('loc_type', '=', 'bat')])
    #
    #         # print('B', len(by_product_fb_obj))
    #         # print('B', len(by_product_mb_obj))
    #         # print('B outer')
    #         if by_product_fb_obj or by_product_mb_obj:
    #             qty_fb = 0
    #             for pro in by_product_fb_obj:
    #                 # print('b', pro.id)
    #                 # print('b', pro.state)
    #                 qty_fb = qty_fb+pro.qty_done
    #
    #             rec.b_actual_ommat_f = qty_fb
    #             # print('b qty_fb', qty_fb)
    #
    #             qty_mb = 0
    #             for pro in by_product_mb_obj:
    #                 qty_mb = qty_mb+pro.qty_done
    #
    #             rec.b_actual_ommat_m = qty_mb


class WBatteryWeek(models.Model):
    _name = 'bat.week.w'
    _description = "Battery Week"

    b_code = fields.Integer('الأسبوع')
    b_code_cww = fields.Integer('الأسبوع للقطيع', store=True)

    b_catalogue_id_ww = fields.Many2one('ommat.catalogue', string="الكتالوج")
    b_flock_id_ww = fields.Many2one('flock.model', string="القطيع")

    b_date_from_ww = fields.Datetime('من')
    b_date_to_ww = fields.Datetime('إلى')

    b_total_age_ww = fields.Integer('العمر الكلى')
    b_productive_age_ww = fields.Integer('العمر الانتاجى')

    b_scraped_f_ww = fields.Float('النافق و الفرزه -انثى', digits=(16, 4))
    b_scraped_m_ww = fields.Float('النافق و الفرزه -ذكر', digits=(16, 4))

    b_scraped_ommat_f_ww = fields.Float('عدد الامهات النافقه -انثى', digits=(16, 4))
    b_scraped_ommat_m_ww = fields.Float('عدد الامهات النافقه -ذكر', digits=(16, 4))

    b_actual_ommat_f_ww = fields.Float('عدد النافق الفعلى -انثى', compute='all_real_bat_no', digits=(16, 4))
    b_actual_ommat_m_ww = fields.Float('عدد النافق الفعلى -ذكر', compute='all_real_bat_no', digits=(16, 4))

    b_rested_ommat_f_ww = fields.Float('عدد الامهات الباقيه -انثى', digits=(16, 4))
    b_rested_ommat_m_ww = fields.Float('عدد الامهات الباقيه -ذكر', digits=(16, 4))

    b_daily_feed_f_ww = fields.Float('جم العلف  -أنثى', digits=(16, 4))
    b_daily_feed_m_ww = fields.Float('جم العلف  -ذكر', digits=(16, 4))

    b_e_daily_feed_f_ww = fields.Float('العلف اليومى -أنثى', digits=(16, 4))
    b_e_daily_feed_m_ww = fields.Float('العلف اليومى -ذكر', digits=(16, 4))

    b_actual_daily_feed_f_ww = fields.Float('العلف الفعلى اليومى -أنثى', compute='all_real_bat_no', digits=(16, 4))
    b_actual_daily_feed_m_ww = fields.Float('العلف الفعلى اليومى -ذكر', compute='all_real_bat_no', digits=(16, 4))

    b_total_weekly_production_f_ww = fields.Float('الانتاج الكلى الاسبوعى ', digits=(16, 4))

    b_total_weekly_production_m_ww = fields.Float('الكلى الاسبوعى القياسى',
                                                  digits=(16, 4))
    b_total_weekly_production_pro_ww = fields.Float('الكلى الاسبوعى الفعلى', compute='all_real_bat_no',
                                                    digits=(16, 4))

    b_evacuation_weekly_production_f_ww = fields.Float('الانتاج التفريغ الاسبوعى ', digits=(16, 4))

    b_evacuation_weekly_production_m_ww = fields.Float('التفريغ الاسبوعى القياسى',
                                                       digits=(16, 4))
    b_evacuation_weekly_production_lab_ww = fields.Float('التفريغ الاسبوعى الفعلى', compute='all_real_bat_no',
                                                         digits=(16, 4))

    b_hatching_f_ww = fields.Float('نسبة الفقس ', digits=(16, 4))

    b_hatching_m_ww = fields.Float('الفقس ', digits=(16, 4))

    # @api.multi
    # def bat_calculate_week_no(self):
    #     init_no = 1
    #     for week in self:
    #         # print('week.l_code =', week.l_code)
    #         week.b_code_cww = init_no
    #         init_no = init_no+1

    # @api.multi
    # @api.depends('b_catalogue_id_ww')
    # def bat_get_rested_ommat_f(self):
    #     last_scraped_f = 1.0
    #     last_rested_f = 1.0
    #     for week in self:
    #         # y = 1.0
    #         if week.b_code == 1:
    #             # اول سطر
    #             x = week.b_catalogue_id_ww.bat_f_num
    #             # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
    #             week.b_scraped_ommat_f_ww = x * week.b_scraped_f_ww
    #
    #             # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
    #             week.b_rested_ommat_f_ww = x-week.b_scraped_ommat_f_ww
    #
    #             last_scraped_f = week.b_scraped_ommat_f_ww
    #             last_rested_f = week.b_rested_ommat_f_ww
    #
    #             # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
    #             week.b_e_daily_feed_f_ww = week.b_rested_ommat_f_ww * week.b_daily_feed_f_ww
    #
    #         else:
    #             # print('a5er kima llscrap =', last_scraped_f)
    #             week.b_scraped_ommat_f_ww = last_rested_f * week.b_scraped_f_ww
    #
    #             last_scraped_f = week.b_scraped_ommat_f_ww
    #             # print('a5er kima llscrap =', last_scraped_f)
    #
    #             week.b_rested_ommat_f_ww = last_rested_f-last_scraped_f
    #
    #             last_rested_f = week.b_rested_ommat_f_ww
    #
    #             # print('اول علف = الباقى - نسبة االعلف', x, week.l_scraped_ommat_f)
    #             week.b_e_daily_feed_f_ww = week.b_rested_ommat_f_ww * week.b_daily_feed_f_ww
    #
    # @api.multi
    # @api.depends('b_catalogue_id_ww')
    # def bat_get_rested_ommat_m(self):
    #     last_scraped_m = 1.0
    #     last_rested_m = 1.0
    #     for week in self:
    #         # y = 1.0
    #         if week.b_code == 1:
    #             # اول سطر
    #             x = week.b_catalogue_id_ww.bat_m_num
    #             # print('اول نافق = عدد الاناث * النسبه', x, week.l_scraped_f)
    #             week.b_scraped_ommat_m_ww = x * week.b_scraped_m_ww
    #
    #             # print('اول باقى = عدد الاناث - نافق', x, week.l_scraped_ommat_f)
    #             week.b_rested_ommat_m_ww = x-week.b_scraped_ommat_m_ww
    #
    #             last_scraped_m = week.b_scraped_ommat_m_ww
    #             last_rested_m = week.b_rested_ommat_m_ww
    #
    #         else:
    #             # print('a5er kima llscrap =', last_scraped_f)
    #             week.b_scraped_ommat_m_ww = last_rested_m * week.b_scraped_m_ww
    #
    #             last_scraped_m = week.b_scraped_ommat_m_ww
    #             # print('a5er kima llscrap =', last_scraped_f)
    #
    #             week.b_rested_ommat_m_ww = last_rested_m-last_scraped_m
    #
    #             last_rested_m = week.b_rested_ommat_m_ww

    @api.multi
    @api.depends('b_code')
    def all_real_bat_no(self):

        scrap_products = self.env['product.product'].search([('scrap', '=', True)])
        feed_products = self.env['product.product'].search([('feed_type', '=', 'feed')])

        for rec in self:
            female_scrap_r_total = 0.0000
            feed_female_r_total = 0.0000
            male_scrap_r_total = 0.0000
            feed_male_r_total = 0.0000

            mo_farming_female = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                                  ('farming', '=', True),

                                                                  ('dynasty', '=', rec.b_catalogue_id_ww.dynasty.id),
                                                                  ('week_no', '=', rec.b_code),
                                                                  ('type_l_b', '=', 'bat')])

            if mo_farming_female:
                for mo in mo_farming_female:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                        for mat in mo.move_raw_ids:
                            if mat.product_id.id in feed_products.ids:
                                feed_female_r_total = feed_female_r_total+mat.quantity_done
                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

                        for mat in mo.move_raw_ids:
                            if mat.product_id.id in feed_products.ids:
                                feed_male_r_total = feed_male_r_total+mat.quantity_done

            production_r_total = 0.000

            mo_production_total = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                                    ('pro', '=', True),

                                                                    ('dynasty', '=', rec.b_catalogue_id_ww.dynasty.id),
                                                                    ('week_no', '=', rec.b_code),
                                                                    ('type_l_b', '=', 'bat')])

            if mo_production_total:
                for mo in mo_production_total:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                production_r_total = production_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                production_r_total = production_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

            evac_r_total = 0.000
            mo_evac_total = rec.env['mrp.production'].search([('state', '=', 'done'),
                                                              ('lab', '=', True),

                                                              ('dynasty', '=', rec.b_catalogue_id_ww.dynasty.id),
                                                              ('week_no', '=', rec.b_code),
                                                              ('type_l_b', '=', 'bat')])

            if mo_evac_total:
                for mo in mo_evac_total:
                    if mo.gender == 'female':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                evac_r_total = evac_r_total+finish.qty_done


                            elif finish.product_id.id in scrap_products.ids:
                                female_scrap_r_total = female_scrap_r_total+finish.qty_done

                    elif mo.gender == 'male':
                        for finish in mo.finished_move_line_ids:
                            if finish.product_id.id not in scrap_products.ids:
                                evac_r_total = evac_r_total+finish.qty_done

                            elif finish.product_id.id in scrap_products.ids:
                                male_scrap_r_total = male_scrap_r_total+finish.qty_done

            rec.b_actual_ommat_f_ww = female_scrap_r_total
            rec.b_actual_ommat_m_ww = male_scrap_r_total
            rec.b_actual_daily_feed_f_ww = feed_female_r_total
            rec.b_actual_daily_feed_m_ww = feed_male_r_total
            rec.b_total_weekly_production_pro_ww = production_r_total
            rec.b_evacuation_weekly_production_lab_ww = evac_r_total
