# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class new_fields_mrp_bom(models.Model):
    _inherit = 'mrp.bom'

    pro = fields.Boolean(related=False, string='Production')
    lab = fields.Boolean(related=False, string='Lab')

    farming = fields.Boolean(default=False, string='Farming')
    cleaning = fields.Boolean(default=False, string='Cleaning')

    @api.multi
    def action_mrp_production(self):
        product = self.product_tmpl_id
        if self.product_tmpl_id.product_variant_ids:
            for p in self.product_tmpl_id.product_variant_ids:
                product = p

        mrp_obj = self.env['mrp.production']

        mo = mrp_obj.create({
            'product_id': product.id,
            'product_qty': self.product_qty,
            'product_uom_id': product.uom_id.id,
            'bom_id': self.id,

        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Manufacturing Orders'),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'mrp.production',
            'res_id': mo.id,
            'target': 'current',

        }


class new_fields_mrp_production(models.Model):
    _inherit = 'mrp.production'

    pro = fields.Boolean(related=False, string='Production')
    lab = fields.Boolean(related=False, string='Lab')
    dynasty = fields.Many2one('dynasty.model', related=False, string='Dynasty')
    gender = fields.Selection([('female', 'Female'),
                               ('male', 'Male')], related=False, copy=False)

    farming = fields.Boolean(default=False, string='Farming')
    cleaning = fields.Boolean(default=False, string='Cleaning')
    type_l_b = fields.Selection([('land', 'Land'), ('bat', 'Battery')], copy=False, default='land', string="Loc Type 1")

    # week_no = fields.Integer('Week No', compute=False, store=True)
    @api.onchange('product_id')
    def onchange_product(self):

        if self.product_id and self.availability == 'waiting':
            self.dynasty = self.product_id.dynasty.id

    @api.onchange('bom_id')
    def onchange_bom(self):

        if self.bom_id and self.availability not in ('assigned', 'partially_available'):
            self.pro = self.bom_id.pro
            self.lab = self.bom_id.lab
            self.farming = self.bom_id.farming
            self.cleaning = self.bom_id.cleaning
            self.gender = self.bom_id.gender

    @api.model
    def create(self, val):
        rec = super(new_fields_mrp_production, self).create(val)

        if rec.bom_id.lab or rec.bom_id.farming or rec.bom_id.pro:

            if rec.product_id:
                if rec.product_id.dynasty:
                    rec.dynasty = rec.product_id.dynasty.id

                    catalogue = rec.env['ommat.catalogue'].search([('dynasty', '=', rec.dynasty.id),
                                                                   ('state', '=', 'in_progress')])
                if rec.type_l_b == 'land':
                    if catalogue and catalogue.land_week_ids:
                        if rec.date_planned_start:
                            p_date = (rec.date_planned_start).date()
                            for line in catalogue.land_week_ids:
                                print(line.l_code)
                                if line.l_date_to and line.l_date_from:
                                    date_f = (line.l_date_from).date()
                                    date_t = (line.l_date_to).date()

                                    if date_f <= p_date <= date_t:
                                        rec.week_no = line.l_code
                            if rec.week_no == 0:
                                raise ValidationError(_('please update catalogue dates'))
                    else:
                        raise ValidationError(_('please update catalogue dates'))
                elif rec.type_l_b == 'bat':
                    if catalogue and catalogue.bat_week_ids:
                        if rec.date_planned_start:
                            p_date = (rec.date_planned_start).date()
                            for line in catalogue.bat_week_ids:
                                print(line.b_code)
                                if line.b_date_to and line.b_date_from:
                                    date_f = (line.b_date_from).date()
                                    date_t = (line.b_date_to).date()

                                    if date_f <= p_date <= date_t:
                                        rec.week_no = line.b_code
                            if rec.week_no == 0:
                                raise ValidationError(_('please update catalogue dates'))

                    else:
                        raise ValidationError(_('please update catalogue dates'))


                else:
                    raise ValidationError(_('please set dynasty for product'))
        return rec

    @api.onchange('location_src_id')
    def onchange_location_src_id(self):

        if self.location_src_id and self.availability not in ('assigned', 'partially_available'):
            for line in self.move_raw_ids:
                line.write({'location_id': self.location_src_id.id})
            if self.location_src_id.type_l_b:
                self.type_l_b = self.location_src_id.type_l_b

    def action_assign(self):

        rec = super(new_fields_mrp_production, self).action_assign()
        if self.availability != 'waiting':
            self.pro = self.bom_id.pro
            self.lab = self.bom_id.lab
            self.farming = self.bom_id.farming
            self.cleaning = self.bom_id.cleaning
            self.gender = self.bom_id.gender
            self.dynasty = self.product_id.dynasty.id
            self.type_l_b = self.location_src_id.type_l_b

        return rec

    @api.one
    @api.depends('date_planned_start')
    def get_week_no(self):
        if self.product_id:
            if self.product_id.dynasty:
                self.dynasty = self.product_id.dynasty.id

                catalogue = self.env['ommat.catalogue'].search([('dynasty', '=', self.dynasty.id),
                                                                ('state', '=', 'in_progress')])
                if self.type_l_b == 'land':
                    if catalogue and catalogue.land_week_ids:
                        if self.date_planned_start:
                            p_date = (self.date_planned_start).date()
                            for line in catalogue.land_week_ids:
                                print(line.l_code)
                                if line.l_date_to and line.l_date_from:
                                    date_f = (line.l_date_from).date()
                                    date_t = (line.l_date_to).date()

                                    if date_f <= p_date <= date_t:
                                        self.week_no = line.l_code
                            if self.week_no == 0:
                                raise ValidationError(_('please update catalogue dates'))

                    else:
                        raise ValidationError(_('please update catalogue dates'))

                elif self.type_l_b == 'bat':
                    if catalogue and catalogue.bat_week_ids:
                        if self.date_planned_start:
                            p_date = (self.date_planned_start).date()
                            for line in catalogue.bat_week_ids:
                                print(line.b_code)
                                if line.b_date_to and line.b_date_from:
                                    date_f = (line.b_date_from).date()
                                    date_t = (line.b_date_to).date()

                                    if date_f <= p_date <= date_t:
                                        self.week_no = line.b_code
                            if self.week_no == 0:
                                raise ValidationError(_('please update catalogue dates'))

                    else:
                        raise ValidationError(_('please update catalogue dates'))



            else:
                raise ValidationError(_('please set dynasty for produced product'))


# class change_ommat_catalogue(models.Model):
#     _inherit = 'ommat.catalogue'
#
#     date_to_first_week = fields.Date('إلى اولاسبوع')
#
#     @api.multi
#     def upload_weeks(self):
#         if self.flock_id:
#             land_week_line = []
#             bat_week_line = []
#             w_land_week_line = []
#             w_bat_week_line = []
#             last_wn_land_week = 0
#             last_wn_bat_week_line = 0
#             last_wn_w_land_week_line = 0
#             last_wn_w_bat_week_line = 0
#
#             if self.land_week_ids:
#
#                 for check_line in self.land_week_ids:
#                     if last_wn_land_week < check_line.l_code:
#                         last_wn_land_week = check_line.l_code
#                         l_date_from = check_line.l_date_from
#                         l_date_to = check_line.l_date_to
#             else:
#                 l_date_from = str(self.date_from)
#                 l_date_to = str(self.date_to_first_week)
#             check = False
#             for line in self.flock_id.land_week_ids:
#                 if line.l_code > last_wn_land_week:
#
#                     if last_wn_land_week != 0:
#                         l_date_from = l_date_to+relativedelta(days=1)
#                         l_date_to = l_date_from+relativedelta(days=7)
#
#                     elif check == True:
#                         l_date_from = fields.Datetime.from_string(l_date_to)+relativedelta(days=1)
#                         l_date_to = fields.Datetime.from_string(l_date_from)+relativedelta(days=7)
#
#                     land_week_line.append((0, 0, {
#                         'l_code': line.l_code,
#                         # 'l_catalogue_id': self.id,
#                         # 'l_flock_id': line.l_flock_id.id,
#                         'l_date_from': l_date_from,
#                         'l_date_to': l_date_to,
#                         'l_total_age': line.l_total_age,
#                         'l_productive_age': line.l_productive_age,
#                         'l_scraped_f': line.l_scraped_f,
#                         'l_scraped_m': line.l_scraped_m,
#                         'l_daily_feed_f': line.l_daily_feed_f,
#                         'l_daily_feed_m': line.l_daily_feed_m,
#                         'l_total_weekly_production_f': line.l_total_weekly_production_f,
#                         'l_evacuation_weekly_production_f': line.l_evacuation_weekly_production_f,
#                         'l_hatching_f': line.l_hatching_f,
#                     }))
#                     check = True
#
#             if self.bat_week_ids:
#                 for check_line in self.bat_week_ids:
#                     if last_wn_bat_week_line < check_line.b_code:
#                         last_wn_bat_week_line = check_line.b_code
#                         b_date_from = check_line.b_date_from
#                         b_date_to = check_line.b_date_to
#             else:
#                 b_date_from = str(self.date_from)
#                 b_date_to = str(self.date_to_first_week)
#             check = False
#             for line in self.flock_id.bat_week_ids:
#                 if line.b_code > last_wn_bat_week_line:
#                     if last_wn_bat_week_line != 0:
#                         b_date_from = b_date_to+relativedelta(days=1)
#                         b_date_to = b_date_from+relativedelta(days=7)
#
#                     elif check == True:
#                         b_date_from = fields.Datetime.from_string(b_date_to)+relativedelta(days=1)
#                         b_date_to = fields.Datetime.from_string(b_date_from)+relativedelta(days=7)
#
#                     bat_week_line.append((0, 0, {
#                         'b_date_from': b_date_from,
#                         'b_date_to': b_date_to,
#                         'b_total_age': line.b_total_age,
#                         'b_productive_age': line.b_productive_age,
#                         'b_scraped_f': line.b_scraped_f,
#                         'b_scraped_m': line.b_scraped_m,
#                         'b_daily_feed_f': line.b_daily_feed_f,
#                         'b_daily_feed_m': line.b_daily_feed_m,
#                         'b_total_weekly_production_f': line.b_total_weekly_production_f,
#                         'b_evacuation_weekly_production_f': line.b_evacuation_weekly_production_f,
#                         'b_hatching_f': line.b_hatching_f,
#                     }))
#                     check = True
#
#             if self.w_land_week_ids:
#                 for check_line in self.w_land_week_ids:
#                     if last_wn_w_land_week_line < check_line.l_code:
#                         last_wn_w_land_week_line = check_line.l_code
#
#             for line in self.flock_id.w_land_week_ids:
#                 if line.l_code > last_wn_w_land_week_line:
#                     w_land_week_line.append((0, 0, {
#                         'l_total_age_ww': line.l_total_age_ww,
#                         'l_productive_age_ww': line.l_productive_age_ww,
#                         'l_scraped_f_ww': line.l_scraped_f_ww,
#                         'l_scraped_m_ww': line.l_scraped_m_ww,
#                         'l_daily_feed_f_ww': line.l_daily_feed_f_ww,
#                         'l_daily_feed_m_ww': line.l_daily_feed_m_ww,
#                         'l_total_weekly_production_f_ww': line.l_total_weekly_production_f_ww,
#                         'l_evacuation_weekly_production_f_ww': line.l_evacuation_weekly_production_f_ww,
#                         # 'l_catalogue_id': self.id,
#                         'l_hatching_f_ww': line.l_hatching_f_ww,
#                     }))
#
#             if self.w_bat_week_ids:
#                 for check_line in self.w_bat_week_ids:
#                     if last_wn_w_bat_week_line < check_line.b_co22de:
#                         last_wn_w_bat_week_line = check_line.b_code
#             for line in self.flock_id.w_bat_week_ids:
#                 if line.b_code > last_wn_land_week:
#                     w_bat_week_line.append((0, 0, {
#                         'b_total_age_ww': line.b_total_age_ww,
#                         'b_productive_age_ww': line.b_productive_age_ww,
#                         'b_scraped_f_ww': line.b_scraped_f_ww,
#                         'b_scraped_m_ww': line.b_scraped_m_ww,
#                         'b_daily_feed_f_ww': line.b_daily_feed_f_ww,
#                         'b_daily_feed_m_ww': line.b_daily_feed_m_ww,
#                         'b_total_weekly_production_f_ww': line.b_total_weekly_production_f_ww,
#                         'b_evacuation_weekly_production_f_ww': line.b_evacuation_weekly_production_f_ww,
#                         'b_hatching_f_ww': line.b_hatching_f_ww,
#                     }))
#             self.update({'land_week_ids': land_week_line,
#                          'bat_week_ids': bat_week_line,
#                          'w_land_week_ids': w_land_week_line,
#                          'w_bat_week_ids': w_bat_week_line
#                          })
#
#             self.land_get_rested_ommat()
#             self.bat_get_rested_ommat()


# class change_LandWeek(models.Model):
#     _inherit = 'land.week'

    # l_actual_ommat_f = fields.Float('عدد النافق الفعلى -انثى', compute='all_real_land_no', digits=(16, 4))
    # l_actual_ommat_m = fields.Float('عدد النافق الفعلى -ذكر', compute='all_real_land_no', digits=(16, 4))
    # l_actual_daily_feed_f = fields.Float('العلف الفعلى اليومى -أنثى', compute='all_real_land_no', digits=(16, 4))
    # l_actual_daily_feed_m = fields.Float('العلف الفعلى اليومى -ذكر', compute='all_real_land_no', digits=(16, 4))
    # l_total_weekly_production_pro = fields.Float('الكلى الاسبوعى الفعلى', compute='all_real_land_no', digits=(16, 4))
    # l_evacuation_weekly_production_lab = fields.Float('التفريغ الاسبوعى الفعلى', compute='all_real_land_no',
    #                                                   digits=(16, 4))

    # @api.multi
    # @api.depends('l_code')
    # def all_real_land_no(self):
    #
    #     scrap_products = self.env['product.product'].search([('scrap', '=', True)])
    #     feed_products = self.env['product.product'].search([('feed_type', '=', 'feed')])
    #
    #     for rec in self:
    #         female_scrap_r_total = 0.0000
    #         feed_female_r_total = 0.0000
    #         male_scrap_r_total = 0.0000
    #         feed_male_r_total = 0.0000
    #
    #         mo_farming_female = rec.env['mrp.production'].search([('state', '=', 'done'),
    #                                                               ('farming', '=', True),
    #
    #                                                               ('dynasty', '=', rec.l_catalogue_id.dynasty.id),
    #                                                               ('week_no', '=', rec.l_code),
    #                                                               ('type_l_b', '=', 'land')])
    #
    #         if mo_farming_female:
    #             for mo in mo_farming_female:
    #                 if mo.gender == 'female':
    #                     for finish in mo.finished_move_line_ids:
    #                         if finish.product_id.id in scrap_products.ids:
    #                             female_scrap_r_total = female_scrap_r_total+finish.qty_done
    #
    #                     for mat in mo.move_raw_ids:
    #                         if mat.product_id.id in feed_products.ids:
    #                             feed_female_r_total = feed_female_r_total+mat.quantity_done
    #                 elif mo.gender == 'male':
    #                     for finish in mo.finished_move_line_ids:
    #                         if finish.product_id.id in scrap_products.ids:
    #                             male_scrap_r_total = male_scrap_r_total+finish.qty_done
    #
    #                     for mat in mo.move_raw_ids:
    #                         if mat.product_id.id in feed_products.ids:
    #                             feed_male_r_total = feed_male_r_total+mat.quantity_done
    #
    #         production_r_total = 0.000
    #
    #         mo_production_total = rec.env['mrp.production'].search([('state', '=', 'done'),
    #                                                                 ('pro', '=', True),
    #
    #                                                                 ('dynasty', '=', rec.l_catalogue_id.dynasty.id),
    #                                                                 ('week_no', '=', rec.l_code),
    #                                                                 ('type_l_b', '=', 'land')])
    #
    #         if mo_production_total:
    #             for mo in mo_production_total:
    #                 if mo.gender == 'female':
    #                     for finish in mo.finished_move_line_ids:
    #                         if finish.product_id.id not in scrap_products.ids:
    #                             production_r_total = production_r_total+finish.qty_done
    #
    #                         elif finish.product_id.id in scrap_products.ids:
    #                             female_scrap_r_total = female_scrap_r_total+finish.qty_done
    #
    #                 elif mo.gender == 'male':
    #                     for finish in mo.finished_move_line_ids:
    #                         if finish.product_id.id not in scrap_products.ids:
    #                             production_r_total = production_r_total+finish.qty_done
    #
    #                         elif finish.product_id.id in scrap_products.ids:
    #                             male_scrap_r_total = male_scrap_r_total+finish.qty_done
    #
    #         evac_r_total = 0.000
    #         mo_evac_total = rec.env['mrp.production'].search([('state', '=', 'done'),
    #                                                           ('lab', '=', True),
    #
    #                                                           ('dynasty', '=', rec.l_catalogue_id.dynasty.id),
    #                                                           ('week_no', '=', rec.l_code),
    #                                                           ('type_l_b', '=', 'land')])
    #
    #         if mo_evac_total:
    #             for mo in mo_evac_total:
    #                 if mo.gender == 'female':
    #                     for finish in mo.finished_move_line_ids:
    #                         if finish.product_id.id not in scrap_products.ids:
    #                             evac_r_total = evac_r_total+finish.qty_done
    #
    #
    #                         elif finish.product_id.id in scrap_products.ids:
    #                             female_scrap_r_total = female_scrap_r_total+finish.qty_done
    #
    #                 elif mo.gender == 'male':
    #                     for finish in mo.finished_move_line_ids:
    #                         if finish.product_id.id not in scrap_products.ids:
    #                             evac_r_total = evac_r_total+finish.qty_done
    #
    #                         elif finish.product_id.id in scrap_products.ids:
    #                             male_scrap_r_total = male_scrap_r_total+finish.qty_done
    #
    #         rec.l_actual_ommat_f = female_scrap_r_total
    #         rec.l_actual_ommat_m = male_scrap_r_total
    #         rec.l_actual_daily_feed_f = feed_female_r_total
    #         rec.l_actual_daily_feed_m = feed_male_r_total
    #         rec.l_total_weekly_production_pro = production_r_total
    #         rec.l_evacuation_weekly_production_lab = evac_r_total


# class change_BatteryWeek(models.Model):
#     _inherit = 'bat.week'
#
#     b_actual_ommat_f = fields.Float('عدد النافق الفعلى -انثى', compute='all_real_bat_no', digits=(16, 4))
#     b_actual_ommat_m = fields.Float('عدد النافق الفعلى -ذكر', compute='all_real_bat_no', digits=(16, 4))
#     b_actual_daily_feed_f = fields.Float('العلف الفعلى اليومى -أنثى', compute='all_real_bat_no', digits=(16, 4))
#     b_actual_daily_feed_m = fields.Float('العلف الفعلى اليومى -ذكر', compute='all_real_bat_no', digits=(16, 4))
#     b_total_weekly_production_pro = fields.Float('الكلى الاسبوعى الفعلى', compute='all_real_bat_no', digits=(16, 4))
#     b_evacuation_weekly_production_lab = fields.Float('التفريغ الاسبوعى الفعلى', compute='all_real_bat_no',
#                                                       digits=(16, 4))
#
#     @api.multi
#     @api.depends('b_code')
#     def all_real_bat_no(self):
#
#         scrap_products = self.env['product.product'].search([('scrap', '=', True)])
#         feed_products = self.env['product.product'].search([('feed_type', '=', 'feed')])
#
#         for rec in self:
#             female_scrap_r_total = 0.0000
#             feed_female_r_total = 0.0000
#             male_scrap_r_total = 0.0000
#             feed_male_r_total = 0.0000
#
#             mo_farming_female = rec.env['mrp.production'].search([('state', '=', 'done'),
#                                                                   ('farming', '=', True),
#
#                                                                   ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
#                                                                   ('week_no', '=', rec.b_code),
#                                                                   ('type_l_b', '=', 'bat')])
#
#             if mo_farming_female:
#                 for mo in mo_farming_female:
#                     if mo.gender == 'female':
#                         for finish in mo.finished_move_line_ids:
#                             if finish.product_id.id in scrap_products.ids:
#                                 female_scrap_r_total = female_scrap_r_total+finish.qty_done
#
#                         for mat in mo.move_raw_ids:
#                             if mat.product_id.id in feed_products.ids:
#                                 feed_female_r_total = feed_female_r_total+mat.quantity_done
#                     elif mo.gender == 'male':
#                         for finish in mo.finished_move_line_ids:
#                             if finish.product_id.id in scrap_products.ids:
#                                 male_scrap_r_total = male_scrap_r_total+finish.qty_done
#
#                         for mat in mo.move_raw_ids:
#                             if mat.product_id.id in feed_products.ids:
#                                 feed_male_r_total = feed_male_r_total+mat.quantity_done
#
#             production_r_total = 0.000
#
#             mo_production_total = rec.env['mrp.production'].search([('state', '=', 'done'),
#                                                                     ('pro', '=', True),
#
#                                                                     ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
#                                                                     ('week_no', '=', rec.b_code),
#                                                                     ('type_l_b', '=', 'bat')])
#
#             if mo_production_total:
#                 for mo in mo_production_total:
#                     if mo.gender == 'female':
#                         for finish in mo.finished_move_line_ids:
#                             if finish.product_id.id not in scrap_products.ids:
#                                 production_r_total = production_r_total+finish.qty_done
#
#                             elif finish.product_id.id in scrap_products.ids:
#                                 female_scrap_r_total = female_scrap_r_total+finish.qty_done
#
#                     elif mo.gender == 'male':
#                         for finish in mo.finished_move_line_ids:
#                             if finish.product_id.id not in scrap_products.ids:
#                                 production_r_total = production_r_total+finish.qty_done
#
#                             elif finish.product_id.id in scrap_products.ids:
#                                 male_scrap_r_total = male_scrap_r_total+finish.qty_done
#
#             evac_r_total = 0.000
#             mo_evac_total = rec.env['mrp.production'].search([('state', '=', 'done'),
#                                                               ('lab', '=', True),
#
#                                                               ('dynasty', '=', rec.b_catalogue_id.dynasty.id),
#                                                               ('week_no', '=', rec.b_code),
#                                                               ('type_l_b', '=', 'bat')])
#
#             if mo_evac_total:
#                 for mo in mo_evac_total:
#                     if mo.gender == 'female':
#                         for finish in mo.finished_move_line_ids:
#                             if finish.product_id.id not in scrap_products.ids:
#                                 evac_r_total = evac_r_total+finish.qty_done
#
#
#                             elif finish.product_id.id in scrap_products.ids:
#                                 female_scrap_r_total = female_scrap_r_total+finish.qty_done
#
#                     elif mo.gender == 'male':
#                         for finish in mo.finished_move_line_ids:
#                             if finish.product_id.id not in scrap_products.ids:
#                                 evac_r_total = evac_r_total+finish.qty_done
#
#                             elif finish.product_id.id in scrap_products.ids:
#                                 male_scrap_r_total = male_scrap_r_total+finish.qty_done
#
#             rec.b_actual_ommat_f = female_scrap_r_total
#             rec.b_actual_ommat_m = male_scrap_r_total
#             rec.b_actual_daily_feed_f = feed_female_r_total
#             rec.b_actual_daily_feed_m = feed_male_r_total
#             rec.b_total_weekly_production_pro = production_r_total
#             rec.b_evacuation_weekly_production_lab = evac_r_total


class changeMrpSubProduct(models.Model):
    _inherit = 'mrp.subproduct'

    mrp_id = fields.Many2one('mrp.production', compute=False)
