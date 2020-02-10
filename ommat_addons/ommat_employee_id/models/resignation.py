from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

from odoo.fields import Date, Datetime


class EmployeeIdResignationOmmat(models.Model):
    _name = 'emp.resignation'


    name=fields.Many2one('hr.employee',string='Employee')
    dept = fields.Many2one('hr.department', string='Department',related='name.department_id')
    emp_id=fields.Char(string='ID',related='name.barcode')
    date_start=fields.Date(string='Start Date')
    total_working_years=fields.Char(string='Total Working Years',compute="_duration_of_years")
    notice_period=fields.Char(string='Notice Period',compute="_duration_of_notice")
    leaving_date=fields.Date(string='Leaving Date')
    confirmation_date=fields.Date(string='Confirmation Date',default=fields.Date.today)
    hr_approval_date=fields.Date(string='HR Approval Date',default=fields.Date.today)
    system_time = fields.Date(string='Today Date',default=fields.Date.today)

    company_id = fields.Many2one('res.company', string='Company' ,default=lambda self: self.env.user.company_id)


    state = fields.Selection([
        ('submit', "Submitted"),
        ('confirmed', "Confirmed"),
        ('approve', "Approved"),

    ], default='submit')

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_approve(self):
        self.state = 'approve'

    @api.multi
    def action_submit(self):
        self.state = 'submit'



    @api.multi
    @api.depends('date_start', 'leaving_date')
    def _duration_of_years(self):
     for rec in self:
        if rec.date_start and rec.leaving_date:

                init_date = dt.strptime(str(rec.date_start), '%Y-%m-%d')
                end_date = dt.strptime(str(rec.leaving_date), '%Y-%m-%d')
                # rec.total_working_years = str((end_date - init_date).days)
                asd= str(relativedelta(end_date, init_date))
                mm=asd.split('(')
                ww=mm[1]
                qq=('('+ww)
                rec.total_working_years=(qq)

    @api.multi
    @api.depends('system_time', 'leaving_date')
    def _duration_of_notice(self):
      for rec in self:
        if rec.leaving_date:
            fmt = '%Y-%m-%d'
            d1 = rec.system_time
            d2 = rec.leaving_date
            # days_between_dates = str((d2 - d1).days)
            # self.notice_period = str(int((int(days_between_dates))))
            asd = str(relativedelta(d2, d1))
            mm = asd.split('(')
            ww = mm[1]
            qq = ('(' + ww)
            rec.notice_period = (qq)





