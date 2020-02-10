
from odoo import fields,models,api

class Bonus(models.TransientModel):

    _inherit = ['bonus','bonus.line']
    _name = 'bounss'

    @api.multi
    def print_report(self):
        return self.env.ref('inventory_report.bonuss_report') .report_action(self)




