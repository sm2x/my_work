# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FlockModel(models.Model):
    _name = 'flock.model'
    _rec_name = 'flock_name'
    _description = "Flock"

    flock_name = fields.Char('إسم القطيع')
    dynasty = fields.Many2one('dynasty.model', string='السلاله')
    # lot_id = fields.Many2one('stock.production.lot', string='رقم القطيع')

    land_week_ids = fields.One2many('land.week', 'l_flock_id', string='أرضى')
    bat_week_ids = fields.One2many('bat.week', 'b_flock_id', string='بطاريات')

    w_land_week_ids = fields.One2many('land.week.w', 'l_flock_id_ww', string='أرضى')
    w_bat_week_ids = fields.One2many('bat.week.w', 'b_flock_id_ww', string='بطاريات')

    @api.onchange('land_week_ids','bat_week_ids','w_land_week_ids','w_bat_week_ids')
    def compute_weeks_code(self):
        init_no_l = 1
        init_no_b = 1
        init_no_lw = 1
        init_no_bw = 1
        for week in self.land_week_ids:
            print(week.l_code)
            week.l_code = init_no_l
            init_no_l = init_no_l+1

        for week in self.bat_week_ids:
            print(week.b_code)
            week.b_code = init_no_b
            init_no_b = init_no_b+1

        for week in self.w_land_week_ids:
            print(week.l_code)
            week.l_code = init_no_lw
            init_no_lw = init_no_lw+1

        for week in self.w_bat_week_ids:
            print(week.b_code)
            week.b_code = init_no_bw
            init_no_bw = init_no_bw+1


class DynastyModel(models.Model):
    _name = 'dynasty.model'
    _rec_name = 'dynasty_name'
    _description = "Dynasty"

    dynasty_name = fields.Integer('السلاله')




