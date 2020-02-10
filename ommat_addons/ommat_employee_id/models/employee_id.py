from random import choice
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError


class EmployeeIdInherit(models.Model):
    _inherit = 'hr.employee'

    leaving_work_reason = fields.Many2one('work.leave',string='Reason for Leaving work')
    loans_agreement =fields.Many2many('ommat.loan')
    military_status = fields.Selection([
        ('exempted', "معفي"),
        ('postopned', "مؤجل"),
        ('completed', "أدي الخدمة"),
        ('under_age', "لم يصبه الدور")
        ], string='Military Status')

    system_time = fields.Date(default=fields.Date.today,store=True,copy=True)
    insurance_years = fields.Float(string='No Of previous insurance years')
    emp_wage = fields.Monetary('Wage', digits=(16, 2), required=True, track_visibility="onchange", help="Employee's monthly gross wage.",default=0)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    work_location = fields.Char('Work Location')
    work_place = fields.Selection([
        ('head_office', "الادارة"),
        ('lap', "معمل"),
        ('project', "مشروع"),
        ('slaughterhouse', "مجزر")
    ], string='Work Location',default='lap')

    emp_date_start = fields.Date('Start Date',help="Start date of the contract.",copy=True)
    contract_type = fields.Many2one('hr.contract.type', string="Contract Type", required=True, default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    contract_date = fields.Date('Contract Date',help="Start date of the contract.",copy=True,default=fields.Date.today,)
    blood_type=fields.Selection([
        ('a+', "A+"),
        ('a-', "A-"),
        ('b+', "B+"),
        ('b-', "B-"),
        ('ab+', "AB+"),
        ('ab-', "AB-"),
        ('o+', "O+"),
        ('o-', "O-"),
    ], string='Blood Type')

    job_type=fields.Selection([
        ('specialist', "موظف متخصص"),
        ('worker', "عامل"),
        ('trainee', "متدرب"),
        ('consultant', "استشاري"),
    ], string='Job Type')

    has_assignments = fields.Boolean(string='Has Assignments?')
    assignments_date_from = fields.Date(string='Assignment Date From')
    assignments_date_to = fields.Date(string='Assignment Date To')
    assignments_value = fields.Monetary(string='Assignment Value',copy=True,store=True)
    assignments_period = fields.Char(string='Assignment Period',compute='get_assignments_duration')

    certificate_level = fields.One2many('certificate.level_bridge','rel_certificate',string='Scientific Certificates')
    family_info = fields.One2many('family.info','family_rel',string='Family')

    @api.multi
    @api.depends('assignments_date_from', 'assignments_date_to')
    def get_assignments_duration(self):
        for rec in self:
         if rec.assignments_date_to:
            fmt = '%Y-%m-%d'
            d1 = rec.assignments_date_from
            d2 = rec.assignments_date_to
            days_between_dates = str((d2 - d1).days)
            rec.assignments_period = str(int((int(days_between_dates))))




    @api.multi
    # @api.onchange('assignments_value','has_assignments')
    def assignments_salary_rule(self):
        for line in self:
            if line.has_assignments == True:
                asd = line.env['hr.contract'].search([('employee_id.name', '=', line.name)])
                for record in asd:
                    record.write({

                        'assignments_value': line.assignments_value,


                    })
                print(asd.assignments_value)

    @api.constrains('active')
    def _check_parent_id(self):
        a = self.system_time
        print(a)
        if self.active == False:
            for l in self.loans_agreement:
                if l.loan_end_date > a:
                    raise ValidationError(
                        _('You cannot archive this employee ,There is a running loan applicable to the employee.'))


class EmployeeIdWorkLeave(models.Model):
    _name = 'work.leave'

    name = fields.Char(string='Reason for Leaving work')



class EmployeeIdCertificateLevel(models.Model):
    _name = 'certificate.level'

    name = fields.Char(string='Certificate Name')


class EmployeeIdSchoolUniversity(models.Model):
    _name = 'school.university'

    name = fields.Char(string='School/University')

class EmployeeIdCertificatePageBridge(models.Model):
    _name = 'certificate.level_bridge'

    certificate_level = fields.Many2one('certificate.level',string='Certificate Level')
    field_of_study = fields.Char(string='Field Of Study')
    school_university = fields.Many2one('school.university',string='School')


    rel_certificate = fields.Many2one('hr.employee')


class EmployeeIdFamilyInfoBridge(models.Model):
    _name = 'family.info'

    name = fields.Char(string='Name')
    relationship = fields.Selection([
        ('father', "أب"),
        ('mother', "أم"),
        ('son', "ابن"),
        ('daughter', "ابنة"),
        ('brother', "أخ"),
        ('sister', "أخت"),
        ('wife/husband', "زوجة/زوج"),
    ], string='Relationship')
    contact_number = fields.Char(string='Contact Number')
    member_birth = fields.Date(string='Member Birthday')
    gender = fields.Selection([
        ('male', "Male"),
        ('female', "Female"),
    ], string='Gender')
    degree = fields.Selection([
        ('primary', "ابتدائية"),
        ('prep', " اعدادية"), ('secondary', "ثانوية"),
        ('bachelor', " بكالوريوس/ليسانس"), ('literacy', " امي"),
        ('postgraduate', "دراسات عليا"), ('doctorate', "دكتوراة"),
        ('ma', "ماجستير"), ('others', "اخري"),
    ], string='Degree')

    chronic_disease = fields.Char(string='امراض مزمنة ان وجدت')



    family_rel=fields.Many2one('hr.employee')

