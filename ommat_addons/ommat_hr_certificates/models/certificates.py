from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError


class EmployeeHROmmatCertificates(models.Model):
    _name = 'hr.certificates'
    _rec_name = 'certificate_type'

    certificate_type=fields.Selection([
        ('concern', "شهادة لمن يهمه الامر"),
        ('free', "شهادة خلو طرف"),
        ('work', "شهادة عمل"),
        ('experience', "شهادة خبرة"),
        ('concern', "شهادة شكر وتقدير"),
        ('social_insurance_fund', "الصندوق القومي للتأمين الاجتماعي"),
        ('free form', "استمارة خلو طرف"),
        ], string='اختر نوع الشهادة')


    emp_name=fields.Many2one('hr.employee',string='الموظف')
    today_date=fields.Date(string='تاريخ اليوم',default=fields.Date.today,readonly=True)
    hr_dept_manager=fields.Many2one('hr.employee',string='مدير الموارد البشرية')
    emp_position=fields.Many2one('hr.job',string='الوظيفة',related='emp_name.job_id')
    leave_start_date=fields.Datetime()
    leave_start_datet=fields.Date()
    end_date=fields.Date(compute='onchange_employee_id_datet')
    leave_end_date=fields.Datetime()
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    gm=fields.Many2one('hr.employee',string='المدير العام')
    text=fields.Text(string='الشكر')

    def onchange_employee_id_datet(self):
        if self.emp_name:
            obj = self.env['emp.resignation'].search([('name', '=', self.emp_name.id)])
            self.end_date= obj.leaving_date

    @api.onchange('leave_start_date','leave_end_date','emp_name')
    def onchange_employee_id_date(self):
        for line in self:
            if line.emp_name:
                asd = self.env['hr.leave.report'].search([('employee_id', '=', line.emp_name.name)])
                for record in asd:
                    self.leave_start_date=record.date_from
                    self.leave_end_date = record.date_to
                    # oo = aa.split()
                    # ww = bb.split()
                    # ee=oo[0]
                    # mm=ww[0]
                    #
                    # self.leave_start_date=ee
                    # self.leave_end_date=mm
