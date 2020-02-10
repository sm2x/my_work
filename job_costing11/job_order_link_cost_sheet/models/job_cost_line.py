# -*- coding: utf-8 -*-

from odoo import models, fields


class JobCostLine(models.Model):
    _inherit = 'job.cost.line'

    # custom_rq_material_id = fields.Many2one(
    #     'material.purchase.requisition.line',
    #     string='Job RQ Material',
    #     readonly=True,
    # )
    #
    custom_material_id = fields.Many2one(
        'material.plan',
        string='Job RQ Material',
        readonly=True,
    )
