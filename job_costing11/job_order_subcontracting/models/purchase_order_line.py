# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _name = 'order.line'

    report_id = fields.Many2one('subcontract.report')

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    taxes_id = fields.Many2many('account.tax', string='Taxes',domain=[('type_tax_use','in', ['business_guarantee','purchase'])])

    list_price = fields.Float('Sale Price', related='product_id.list_price')
    description = fields.Char(
        string='Description',
        required=True,
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
    )
    uom_id = fields.Many2one(
        'product.uom',
        string='Uom',
        required=True,
    )
    sub_contractor_id = fields.Many2one(
        'project.task',
        string='Sub Contractor',
    )
    job_cost_id = fields.Many2one(
        'job.costing',
        string='Job Cost',
    )
    job_cost_line_id = fields.Many2one(
        'job.cost.line',
        string='Job Cost Line',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        related='sub_contractor_id.project_id.analytic_account_id',
    )
    is_created = fields.Boolean(
        string='Purchase order created',
        copy=False,
        readonly=True,
        default=False,
    )

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            # rec.quantity = 1
            rec.uom_id = rec.product_id.uom_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
