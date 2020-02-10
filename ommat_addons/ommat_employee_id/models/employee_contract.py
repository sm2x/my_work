from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError


class EmployeeIdContractInherit(models.Model):
    _inherit = 'hr.contract'

    date_start = fields.Date('Start Date', required=True, default=fields.Date.today,
                             help="Start date of the contract.",copy=True)

    assignments_value = fields.Monetary(string='Assignment Value',store=True,copy=True)
    deduction_value = fields.Monetary(string='Deduction Value',store=True,copy=True)

    # @api.multi
    # def write(self, values):
    #     for l in self:
    #                 asd=self.env['hr.employee'].search([('name', '=', self.employee_id.name)])
    #                 # print(name)
    #                 # print(emp_date_start)
    #                 # print(self.employee_id)
    #                 # print(self.date_start)
    #                 asd.values = {
    #
    #                     'emp_date_start': l.date_start,
    #
    #                 }
    #
    #                 return super(EmployeeIdContractInherit, self).write(values)
    # @api.multi


    @api.onchange('state','employee_id.emp_date_start','date_start','employee_id.contract_type','type_id','employee_id.emp_wage','wage')
    def onchange_employee_id_date(self):
     for line in self:
        if self.state == 'open':
            asd = self.env['hr.employee'].search([('name', '=', line.employee_id.name)])
            for record in asd:
                record.write({

                        # 'emp_date_start': line.date_start,
                        'contract_type': line.type_id.id,
                        'emp_wage': line.wage,
                        'emp_date_start':line.date_start


                })
