
from odoo import fields,models,api


class ProductsWizard(models.TransientModel):
    _name = 'products.wizard'
    # _rec_name = "Products"

    products_ids = fields.Many2many('product.product', string='Products')

    @api.multi
    def print_report(self):
        return self.env.ref('sprogroup_purchase_request.product_list_report') .report_action(self)




