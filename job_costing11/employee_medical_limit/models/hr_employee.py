from odoo import fields, models


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    medical_limit = fields.Float(string="Medical Limits")
