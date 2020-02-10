from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.fields import Datetime


class OmmatEstimation(models.Model):
    _name = 'ommat.catalogue'

    strain = fields.Many2one('product.product', string="السلالة")
    gender = fields.Many2one('product.product', string="النوع")
    bran_type = fields.Many2one('product.product', string="نوع الحظيرة")
    fiscal_year = fields.Many2one('account.fiscal.year', string="السنة المالية ")

    catalouge_relation_company = fields.One2many('company.bridge', 'rel_estimation', string='كتالوج الشركة ')
    catalouge_relation_strain = fields.One2many('strain.bridge', 'rel_estimation', string='كتالوج السلالة')
    lot_no_omat = fields.Many2one('stock.production.lot', string='Lot/Serial Number')
    catalogue_date = fields.Date('Catalogue Date')

    @api.onchange('catalouge_relation_company')
    def calculate_from_dates(self):
        init_from = self.catalogue_date
        for line in self.catalouge_relation_company:
            line.date_from = init_from
            init_from = line.date_to

    @api.onchange('catalouge_relation_company')
    def calculate_to_dates(self):
        for line in self.catalouge_relation_company:
            dt = line.date_from
            new_due_date = dt + timedelta(days=7)
            line.date_to = new_due_date

    @api.onchange('catalouge_relation_company')
    def calculate_week_no(self):
            init_no = 1
            for line in self.catalouge_relation_company:
                line.week_no = init_no
                init_no = init_no + 1

    @api.onchange('catalouge_relation_strain')
    def calculate_strain_from_dates(self):
        init_from = self.catalogue_date
        for line in self.catalouge_relation_strain:
            line.date_from = init_from
            init_from = line.date_to

    @api.onchange('catalouge_relation_strain')
    def calculate_strain_to_dates(self):
        for line in self.catalouge_relation_strain:
            dt = line.date_from
            new_due_date = dt + timedelta(days=7)
            line.date_to = new_due_date

    @api.onchange('catalouge_relation_strain')
    def calculate_strain_week_no(self):
        init_no = 1
        for line in self.catalouge_relation_strain:
            line.week_no = init_no
            init_no = init_no + 1



class OmmatEstimationBridgeCompany(models.Model):
    _name = 'company.bridge'

    rel_estimation = fields.Many2one('ommat.catalogue')
    date_from = fields.Date("From", compute='calculate_from_dates')
    date_to = fields.Date("To", compute='calculate_to_dates')
    week_no = fields.Char(string='رقم اﻻسبوع', compute='calculate_week_no')
    production_age = fields.Char(string='العمر اﻻنتاجي')
    scrap = fields.Char(string='النافق')
    biological_feed_units = fields.Char(string='العلف البيولوجي بالوحدات')
    total_production = fields.Char(string='اﻻنتاج الكلي')
    output_for_unloading = fields.Char(string='اﻻنتاج الصالح للتفريغ')
    hatching = fields.Char(string='الفقس')
    wieght = fields.Char(string='الوزن')

    int_from = fields.Date(string="Date", related='rel_estimation.catalogue_date')


class OmmatEstimationBridgeStrain(models.Model):
    _name = 'strain.bridge'

    rel_estimation = fields.Many2one('ommat.catalogue')
    date_from = fields.Date("From", compute='calculate_strain_from_dates',)
    date_to = fields.Date("To", compute='calculate_strain_to_dates')
    week_no = fields.Char(string='رقم اﻻسبوع', compute='calculate_strain_week_no')
    production_age = fields.Char(string='العمر اﻻنتاجي')
    scrap = fields.Char(string='النافق')
    biological_feed_units = fields.Char(string='العلف البيولوجي بالوحدات')
    total_production = fields.Char(string='اﻻنتاج الكلي')
    output_for_unloading = fields.Char(string='اﻻنتاج الصالح للتفريغ')
    hatching = fields.Char(string='الفقس')
    wieght = fields.Char(string='الوزن')


    