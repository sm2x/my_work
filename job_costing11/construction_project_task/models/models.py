# -*- coding: utf-8 -*-
from AptUrl.Helpers import _

from addons.account.models.account_payment import MAP_INVOICE_TYPE_PAYMENT_SIGN, MAP_INVOICE_TYPE_PARTNER_TYPE
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    rq_clicked = fields.Boolean()

    @api.multi
    def create_RQ(self):
        rq_object = self.env['material.purchase.requisition']
        today = fields.Date.today()
        job_cost = self.env['job.costing'].search([('number', '=', self.job_number)])
        rm_object = self.material_plan_ids
        rq_lines = []

        for line in rm_object:
            rq_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'description': line.description,
                'requisition_type': '',
                'qty': line.product_uom_qty,
                'uom': line.product_uom.id,
                'planned_qty': line.product_uom_qty,
                'custom_job_costing_id': job_cost.id
            }))

        rq_object.create({
            'state': 'draft',
            'request_date': today,
            'employee_id': self.user_id.id,
            'task_id': self.id,
            'requisition_line_ids': rq_lines

        })
        self.rq_clicked = True


class JobCostSheetUpdateWizard(models.TransientModel):
    _inherit = "jobcostsheet.update.wizard"

    @api.multi
    def create_edit_jobcostsheet(self):
        active_id = self._context.get('active_id')
        project_task_obj = self.env['project.task'].browse(active_id)
        job_type = self.env['job.type'].search([('name', '=', 'Material')])
        job_cost_line = self.env['job.cost.line']
        job_costsheet = self.env['job.costing']
        # rq_lines = []

        if self.costsheet_type == 'create_costsheet':
            for material in project_task_obj.material_plan_ids:
                flag1 = False
                if not material.is_material_created:
                    flag1 = False
                    break
                else:
                    flag1 = True
            if flag1:
                raise Warning(_('No Material Line Found.'))
            costsheet_vals = {
                'name': 'New',
                'project_id': project_task_obj.project_id.id,
                'analytic_id': project_task_obj.project_id.analytic_account_id.id,
                'partner_id': project_task_obj.partner_id.id,
                'task_id': project_task_obj.id,
                'state': 'draft',
            }
            costsheet = job_costsheet.create(costsheet_vals)

            # for material in project_task_obj.material_plan_ids:
            #     if not material.is_material_created:
            #         for line in project_task_obj.move_ids.filtered(lambda p: p.product_id.id == material.product_id.id):
            #             # .filtered(lambda p: p.product_id.id == line.product_id.id)
            #             rq_lines.append((0, 0, {
            #                 'product_id': line.product_id.id,
            #                 'description': line.description,
            #                 'requisition_type': line.requisition_type,
            #                 'uom': line.uom.id,
            #                 'qty': line.qty
            #             }))

            for material in project_task_obj.material_plan_ids:
                if not material.is_material_created:
                    print("outer")
                    print(material.product_id.id)
                    print(material.product_id.name)

                    rq_lines = []
                    for line in project_task_obj.move_ids.filtered(lambda p: p.product_id.id == material.product_id.id):
                        # .filtered(lambda p: p.product_id.id == line.product_id.id)
                        print("inner")
                        print(material.product_id.id)
                        print(material.product_id.name)
                        # print(material.product_id.id)
                        rq_lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'description': line.description,
                            'requisition_type': line.requisition_type,
                            'uom': line.uom.id,
                            'qty': line.qty
                        }))

                    material_line_vals = {
                        'date': fields.date.today(),
                        'job_type_id': job_type.id,
                        'job_type': 'material',
                        'product_id': material.product_id.id,
                        'product_qty': material.product_uom_qty,
                        'sale_price': material.product_id.list_price,
                        'cost_price': material.product_id.standard_price,
                        'uom_id': material.product_uom.id,
                        'description': material.product_id.name,
                        'direct_id': costsheet.id,
                        'custom_material_id': material.id,
                        'custom_mpr_line_ids': rq_lines
                    }

                    job_costing_material_line = job_cost_line.create(material_line_vals)
                    material.custom_material_job_id = job_costing_material_line.id
                    material.is_material_created = True

        else:
            if project_task_obj.material_plan_ids:
                if self.job_costsheet_id:
                    for material in project_task_obj.material_plan_ids:
                        flag = False
                        if not material.is_material_created:
                            flag = False
                            break
                        else:
                            flag = True
                    if flag:
                        raise Warning(_('No Material Line Found.'))
                    for material in project_task_obj.material_plan_ids:
                        if not material.is_material_created:
                            vals = {
                                'date': fields.date.today(),
                                'job_type_id': job_type.id,
                                'job_type': 'material',
                                'product_id': material.product_id.id,
                                'product_qty': material.product_uom_qty,
                                'uom_id': material.product_uom.id,
                                'description': material.product_id.name,
                                'direct_id': self.job_costsheet_id.id,
                                'custom_material_id': material.id
                            }
                            job_costing_material_line = job_cost_line.create(vals)
                            material.custom_material_job_id = job_costing_material_line.id
                            material.is_material_created = True


class DiefSubContractor(models.TransientModel):
    _inherit = 'sub.contractor'

    @api.multi
    @api.onchange('name')
    def get_user_id(self):
        for rec in self:
            if rec.name:
                task_id = rec._context.get('active_id', False)
                task = rec.env['project.task'].browse(task_id)
                rec.user_id = task.user_id


class DiefAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # payment_guarantee_id = fields.Many2one('payment.guarantee')

    new_total = fields.Monetary("Total Without BG", compute='_compute_new_total')
    total_bg = fields.Monetary("Total BG", compute='_compute_new_total')
    bg_paid = fields.Boolean()

    @api.multi
    @api.onchange('type')
    def get_project(self):
        if self.type == "in_invoice":
            active_id = self._context.get('active_id')
            p_id = self.env['purchase.order'].browse(active_id)
            # p_id = self.env['purchase.order'].search([('id', '=', self.purchase_id)])
            self.project_id = p_id.project_id

    @api.onchange('tax_line_ids', 'amount_total')
    def _compute_new_total(self):
        # global amount_bg_tax
        for inv in self:
            round_curr = inv.currency_id.round
            amount_bg_tax = sum(round_curr(line.amount_total) for line in
                                inv.tax_line_ids.filtered(lambda t: t.business_guarantee == True))

            inv.total_bg = amount_bg_tax
            inv.new_total = inv.amount_total-amount_bg_tax


class DiefPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one('project.project', string='Project')
    bill_clicked = fields.Boolean()
    desc = fields.Text('Description')

    @api.multi
    def create_bill(self):
        for rec in self:
            bill = self.env['account.invoice']
            bill_invoice_line = []

            for line in rec.order_line:
                print('in invoice line')
                bill_invoice_line.append((0, 0, {
                    'invoice_id': bill.id,
                    'purchase_id': rec.id,
                    'purchase_line_id': line.id,
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'quantity': line.product_qty,
                    'uom_id': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_unit,
                    'account_id': rec.product_id.property_account_expense_id.id,
                    'invoice_line_tax_ids': [(6, 0, [x.id for x in line.taxes_id])],
                }))
                # print('line.taxes_id.ids', line.taxes_id.name)

            bill_vals = {
                'partner_id': rec.partner_id.id,
                'origin': rec.name,
                'type': 'in_invoice',
                'purchase_id': rec.id,
                'project_id': rec.project_id.id,
                # 'state': 'open'
                'invoice_line_ids': bill_invoice_line,
            }
            bill.create(bill_vals)
            rec.bill_clicked = True


class DiefPurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    custom_requisition = fields.Many2one('material.purchase.requisition')





class DiefMaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    purchase_order_ids = fields.One2many(
        'purchase.requisition',
        'custom_requisition',
        string='Purchase Agreement',
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        copy=True,
    )

    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approved'),
        ('approve', 'Approved'),
        ('stock', 'Picking Created'),
        ('Purchase', 'Purchase Order Created'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft',
        track_visibility='onchange',
    )
    po_checked = fields.Boolean(copy=False)
    pick_checked = fields.Boolean(copy=False)
    tender_checked = fields.Boolean(copy=False)

    @api.multi
    def request_tender(self):

        tender_obj = self.env['purchase.requisition']
        tender_line_obj = []
        tender_dict = {}

        for rec in self:
            if not rec.requisition_line_ids:
                raise ValidationError(_('Please create some requisition lines.'))

            # if not any(line.requisition_type == 'purchase' for line in rec.requisition_line_ids):
            #     raise ValidationError(_('No Purchase lines.'))
            for line in rec.requisition_line_ids:
                if line.requisition_type == 'purchase':
                    tender_line_obj.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_qty': line.qty,
                        'product_uom_id': line.uom.id,
                        'date_planned': fields.Date.today(),
                        'price_unit': line.product_id.lst_price,
                        # 'requisition_id': rec.id,
                        'account_analytic_id': self.analytic_account_id.id
                    }))

            tender_vals = {
                'currency_id': rec.env.user.company_id.currency_id.id,
                'date_order': fields.Date.today(),
                'company_id': rec.env.user.company_id.id,
                'custom_requisition_id': rec.id,
                'origin': rec.name,
                'custom_requisition': rec.id,
                'line_ids': tender_line_obj
            }
            tender_obj.create(tender_vals)
            self.tender_checked = True

    @api.multi
    def action_view_tender(self):
        for rec in self:
            action = self.env.ref('purchase_requisition.action_purchase_requisition').read()[0]
            action['domain'] = str([('custom_requisition', '=', rec.id)])

            return action

    @api.multi
    def action_email_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''

        print('kkkkkkkkk')
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('construction_project_task', 'dief_email_template_edi_req')[1]
        compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]

        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'material.purchase.requisition',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "dief_mail_template_data_notification_email_purchase_order",
            # 'purchase_mark_rfq_sent': True,
            'force_email': True
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    @api.multi
    def request_po(self):
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        po_dict = {}

        for rec in self:
            if not rec.requisition_line_ids:
                raise ValidationError(_('Please create some requisition lines.'))

            # if not any(line.requisition_type == 'purchase' for line in rec.requisition_line_ids):
            #     raise ValidationError(_('No Purchase lines.'))

            for line in rec.requisition_line_ids:
                if line.requisition_type == 'purchase':
                    if not line.partner_id:
                        raise ValidationError(_('PLease Enter At least One Vendor on Requisition Lines'))

                    for partner in line.partner_id:
                        if partner not in po_dict:
                            po_vals = {
                                'partner_id': partner.id,
                                'currency_id': rec.env.user.company_id.currency_id.id,
                                'date_order': fields.Date.today(),
                                'company_id': rec.env.user.company_id.id,
                                'custom_requisition_id': rec.id,
                                'origin': rec.name,
                                'task_id': rec.task_id.id,
                                'project_id': rec.task_id.project_id.id,
                            }
                            purchase_order = purchase_obj.create(po_vals)
                            po_dict.update({partner: purchase_order})
                            po_line_vals = rec._prepare_po_line(line, purchase_order)

                            purchase_line_obj.sudo().create(po_line_vals)
                            rec.action_email_send()
                            print(purchase_order.name)
                            # purchase_order.action_rfq_send()
                        else:
                            purchase_order = po_dict.get(partner)
                            po_line_vals = rec._prepare_po_line(line, purchase_order)
                            purchase_line_obj.sudo().create(po_line_vals)
                            print(purchase_order.name)
                            rec.action_email_send()
                            # purchase_order.action_rfq_send()

                        rec.state = 'Purchase'

            # purchase_obj.action_rfq_send()
            rec.po_checked = True

    @api.multi
    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']

        for rec in self:
            if not rec.requisition_line_ids:
                raise Warning('Please create some requisition lines.')
            if not any(line.requisition_type == 'internal' for line in rec.requisition_line_ids):
                raise ValidationError(_('No Internal lines.'))
            if any(line.requisition_type == 'internal' for line in rec.requisition_line_ids):
                if not rec.location_id.id:
                    raise ValidationError(_('Select Source location under the picking details.'))
                if not rec.custom_picking_type_id.id:
                    raise ValidationError(_('Select Picking Type under the picking details.'))
                if not rec.dest_location_id:
                    raise ValidationError(_('Select Destination location under the picking details.'))
                #                 if not rec.employee_id.dest_location_id.id or not rec.employee_id.department_id.dest_location_id.id:
                #                     raise Warning(_('Select Destination location under the picking details.'))
                picking_vals = {
                    'partner_id': rec.employee_id.address_home_id.id,
                    'min_date': fields.Date.today(),
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                    'picking_type_id': rec.custom_picking_type_id.id,  # internal_obj.id,
                    'note': rec.reason,
                    'custom_requisition_id': rec.id,
                    'origin': rec.name,
                }
                stock_id = stock_obj.sudo().create(picking_vals)
                delivery_vals = {
                    'delivery_picking_id': stock_id.id,
                }
                rec.write(delivery_vals)

            for line in rec.requisition_line_ids:
                if line.requisition_type == 'internal':
                    pick_vals = rec._prepare_pick_vals(line, stock_id)
                    move_id = move_obj.sudo().create(pick_vals)

                rec.state = 'stock'
        self.pick_checked = True


class SubcontractReport(models.Model):
    _name = "subcontract.report"

    name = fields.Many2one("res.partner", string='Second party', domain="[('supplier', '=', True)]")
    engineer = fields.Many2one("res.users", string='Project Engineer', related='project.user_id')
    project = fields.Many2one('project.project', 'Project')
    payment_term = fields.Many2one("account.payment.term", string='Payment Term')
    business_guarantee = fields.Float('Business Guarantee')
    job_order = fields.Many2one('project.task', 'Job Orders', domain="[('project_id', '=', project)]")
    order_line = fields.One2many('order.line', 'report_id', string='Order Lines')
    penal_conditions = fields.Text("Penal conditions")
    update_clicked = fields.Boolean(copy=False)

    @api.multi
    def update_job_order(self):
        order_line_ids = []
        # self.job_order.purchaseorder_line_ids
        for line in self.order_line:
            order_line_ids.append((0, 0, {
                'product_id': line.product_id.id,
                'description': line.description,
                # 'analytic_account_id': line.analytic_account_id.id,
                'quantity': line.quantity,
                'uom_id': line.uom_id.id,
                'list_price': line.product_id.list_price,
                'taxes_id': line.taxes_id,

            }))

        # res.update({'picking_id': picking.id})
        self.job_order.update({'purchaseorder_line_ids': order_line_ids})
        self.update_clicked = True


class DiefResPartner(models.Model):
    _inherit = 'res.partner'

    vir = fields.Boolean('Is Virtual')


class DiefAccountTax(models.Model):
    _inherit = 'account.tax'

    type_tax_use = fields.Selection([('sale', 'Sales'), ('purchase', 'Purchases'),
                                     ('business_guarantee', 'Business Guarantee'), ('none', 'None')],
                                    string='Tax Scope', required=True, default="sale",
                                    help="Determines where the tax is selectable. Note : 'None' means a tax can't be used by itself, however it can still be used in a group.")

    business_guarantee = fields.Boolean('Business Guarantee')


class DiefAccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    business_guarantee = fields.Boolean('Business Guarantee', related='tax_id.business_guarantee')


class DiefProjectTaskMergeWizard(models.TransientModel):
    _inherit = 'project.task.merge.wizard'

    @api.multi
    def merge_tasks(self):
        values = {
            'user_id': self.user_id.id,
            'description': self.merge_description(),
        }

        if self.create_new_task:

            mpl_lines = []
            mpr_lines = []
            mprl = []
            for task in self.task_ids:
                for mpl in task.material_plan_ids:
                    mpl_lines.append((0, 0, {
                        'product_id': mpl.product_id.id,
                        'product_uom_qty': mpl.product_uom_qty,
                        'product_uom': mpl.product_uom.id,
                        'material_task_id': mpl.material_task_id.id,
                        'custom_material_job_id': mpl.custom_material_job_id.id,
                        'custom_job_cost_id': mpl.custom_job_cost_id.id,
                        'description': mpl.description
                    }))

            for task in self.task_ids:
                for mpr in task.picking_ids:
                    for r_line in mpr.requisition_line_ids:
                        mprl.append((0, 0, {
                            'requisition_id': r_line.requisition_id.id,
                            'product_id': r_line.product_id.id,
                            'description': r_line.description,
                            'qty': r_line.qty,
                            'uom': r_line.uom.id,
                            'partner_id': r_line.partner_id.id,
                            'requisition_type': r_line.requisition_type,
                            'planned_qty': r_line.planned_qty,
                            'custom_job_costing_id': r_line.custom_job_costing_id.id,
                            'custom_job_costing_line_id': r_line.custom_job_costing_line_id.id,

                        }))

                    mpr_lines.append((0, 0, {
                        'name': mpr.name,
                        'state': mpr.state,
                        'request_date': mpr.request_date,
                        'department_id': mpr.department_id.id,
                        'employee_id': mpr.employee_id.id,
                        'approve_manager_id': mpr.approve_manager_id.id,
                        'reject_manager_id': mpr.reject_manager_id.id,
                        'approve_employee_id': mpr.approve_employee_id.id,
                        'reject_employee_id': mpr.reject_employee_id.id,
                        'company_id': mpr.company_id.id,
                        'location_id': mpr.location_id.id,
                        'requisition_line_ids': mprl,
                        'date_end': mpr.date_end,
                        'date_done': mpr.date_done,
                        'analytic_account_id': mpr.analytic_account_id.id,
                        'dest_location_id': mpr.dest_location_id.id,
                        'delivery_picking_id': mpr.delivery_picking_id.id,
                        'requisiton_responsible_id': mpr.requisiton_responsible_id.id,
                        'employee_confirm_id': mpr.employee_confirm_id.id,
                        'confirm_date': mpr.confirm_date,
                        # 'purchase_order_ids': po_lines,
                        'custom_picking_type_id': mpr.custom_picking_type_id.id,
                        'task_id': mpr.task_id.id,
                        'project_id': mpr.project_id.id

                    }))

            values.update({
                'name': self.target_task_name,
                'project_id': self.target_project_id.id,
                'material_plan_ids': mpl_lines,
                'picking_ids': mpr_lines
            })

            self.target_task_id = self.env['project.task'].create(values)
        else:
            self.target_task_id.write(values)
        self.merge_followers()
        self.target_task_id.message_post_with_view(
            self.env.ref('project.mail_template_task_merge'),
            values={'target': True, 'tasks': self.task_ids-self.target_task_id},
            subtype_id=self.env.ref('mail.mt_comment').id
        )
        (self.task_ids-self.target_task_id).message_post_with_view(
            self.env.ref('project.mail_template_task_merge'),
            values={'target': False, 'task': self.target_task_id},
            subtype_id=self.env.ref('mail.mt_comment').id
        )
        (self.task_ids-self.target_task_id).write({'active': False})
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "views": [[False, "form"]],
            "res_id": self.target_task_id.id,
        }


class DiefJobCosting(models.Model):
    _inherit = 'job.costing'

    @api.multi
    def show_requisition(self):
        self.ensure_one()
        task_id = self._context.get('active_id', False)
        task = self.env['project.task'].browse(task_id)
        res = self.env.ref('odoo_job_costing_management.action_material_purchase_requisition_job_costing')
        res = res.read()[0]
        res['domain'] = {'task_id': [('id', 'in', task.ids)]}
        # res['domain'] = str([('task_id', 'in', task.ids)])
        return res


class PaymentBusinessGuaranteeLine(models.Model):
    _name = "payment.guarantee.line"

    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    payment_guarantee_id = fields.Many2one('payment.guarantee')

    number = fields.Char(related='invoice_id.number', string='Number')
    type = fields.Selection(related='invoice_id.type', string='Type')
    state = fields.Selection(related='invoice_id.state', string='State')
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    total_bg = fields.Monetary(related='invoice_id.total_bg', string='Total BG', currency_field='currency_id')
    project_id = fields.Many2one(related='invoice_id.project_id', string='Project')
    job_cost_id = fields.Many2one(related='invoice_id.job_cost_id', string='Job Cost Sheet')


class PaymentBusinessGuarantee(models.Model):
    _name = "payment.guarantee"

    name = fields.Char('name')

    project_id = fields.Many2one('project.project', string='Project')
    currency_id = fields.Many2one(related='project_id.currency_id')

    invoice_type = fields.Selection([
        ('bill', 'Vendor Bill'),
        ('invoice', 'Customer Invoice')], string='Invoice Type')

    invoice_state = fields.Selection([
        ('open', 'Open')], string='Invoice State')

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])

    payment_guarantee_line_ids = fields.One2many('payment.guarantee.line', 'payment_guarantee_id', string='Invoices')
    total = fields.Monetary("Total", compute='compute_total', currency_field='currency_id')
    upload_clicked = fields.Boolean()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid')], default='draft')

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('payment.guarantee.seq')
        })
        return super(PaymentBusinessGuarantee, self).create(vals)

    @api.multi
    def approve_payment(self):
        for rec in self:
            rec.state = 'approved'

    @api.multi
    def compute_total(self):
        for rec in self:
            amount_bg_tax = 0
            for inv in rec.payment_guarantee_line_ids:
                # round_curr = inv.invoice_id.currency_id.round
                # += inv.total_bg
                amount_bg_tax += inv.total_bg
                print('inv.total_bg', inv.total_bg)

            rec.total = amount_bg_tax

    @api.multi
    def upload_invoices(self):
        for rec in self:
            bills = []
            if rec.payment_guarantee_line_ids:
                rec.payment_guarantee_line_ids.unlink()

            inv = rec.env['account.invoice'].search([('project_id', '=', rec.project_id.id),
                                                     ('bg_paid', '=', False)])

            bills_open = rec.env['account.invoice'].search([('project_id', '=', rec.project_id.id),
                                                            ('type', '=', 'in_invoice'),
                                                            ('state', '=', 'open'),
                                                            ('bg_paid', '=', False)])

            # bills_paid = rec.env['account.invoice'].search([('project_id', '=', rec.project_id.id),('type', '=', 'in_invoice'), ('state', '=', 'paid')])
            # bills_all = rec.env['account.invoice'].search([('project_id', '=', rec.project_id.id),('type', '=', 'in_invoice')])

            invoices_open = rec.env['account.invoice'].search([('project_id', '=', rec.project_id.id),
                                                               ('type', '=', 'out_invoice'),
                                                               ('state', '=', 'open'),
                                                               ('bg_paid', '=', False)])

            # invoices_paid = rec.env['account.invoice'].search([('project_id', '=', rec.project_id.id),('type', '=', 'out_invoice'), ('state', '=', 'paid')])
            # invoices_all = rec.env['account.invoice'].search([('project_id', '=', rec.project_id.id),('type', '=', 'out_invoice')])

            if not inv:
                raise ValidationError('There is no invoices for this project yet')

            if rec.invoice_type == 'bill':
                if rec.invoice_state == 'open':

                    if not bills_open:
                        raise ValidationError('There is no open bills for this project')

                    for bill in bills_open:
                        if bill.new_total:
                            bills.append((0, 0, {
                                'invoice_id': bill.id,

                            }))

                # if rec.invoice_state == 'paid':
                #     if not bills_paid:
                #         raise ValidationError('There is no paid bills for this project')
                #
                #     for bill in bills_paid:
                #         bills.append((0, 0, {
                #             'invoice_id': bill.id,
                #
                #         }))
                #
                # if rec.invoice_state == 'all':
                #     if not bills_all:
                #         raise ValidationError('There is no bills for this project')
                #
                #     for bill in bills_all:
                #         bills.append((0, 0, {
                #             'invoice_id': bill.id,
                #
                #         }))

            if rec.invoice_type == 'invoice':
                if rec.invoice_state == 'open':
                    if not invoices_open:
                        raise ValidationError('There is no open Invoices for this project')

                    for bill in invoices_open:
                        if bill.new_total:
                            bills.append((0, 0, {
                                'invoice_id': bill.id,

                            }))

                # if rec.invoice_state == 'paid':
                #     if not invoices_paid:
                #         raise ValidationError('There is no paid Invoices for this project')
                #
                #     for bill in invoices_paid:
                #         bills.append((0, 0, {
                #             'invoice_id': bill.id,
                #
                #         }))
                #
                # if rec.invoice_state == 'all':
                #     if not invoices_all:
                #         raise ValidationError('There is no Invoices for this project')
                #
                #     for bill in invoices_all:
                #         bills.append((0, 0, {
                #             'invoice_id': bill.id,
                #
                #         }))

            # if rec.invoice_type == 'all':
            #     rec.invoice_state = 'all'
            #     for bill in inv:
            #         bills.append((0, 0, {
            #             'invoice_id': bill.id,
            #
            #         }))

            rec.payment_guarantee_line_ids = bills

    @api.one
    def create_payment(self):
        for rec in self:
            if rec.payment_guarantee_line_ids:
                for line in rec.payment_guarantee_line_ids:
                    statment_obj = rec.env['account.payment']

                    if rec.invoice_type == 'bill':
                        vals = {
                            'payment_type': 'outbound',
                            'partner_type': 'supplier',
                            'partner_id': line.invoice_id.partner_id.id,
                            'amount': line.total_bg,
                            'currency_id': line.currency_id.id,
                            'journal_id': rec.journal_id.id,
                            'payment_date': line.invoice_id.date_invoice,
                            'communication': 'BG/'+line.number,
                            'payment_method_id': rec.journal_id.outbound_payment_method_ids.id

                        }
                    else:
                        vals = {
                            'payment_type': 'inbound',
                            'partner_type': 'customer',
                            'partner_id': line.invoice_id.partner_id.id,
                            'amount': line.total_bg,
                            'currency_id': line.currency_id.id,
                            'journal_id': rec.journal_id.id,
                            'payment_date': line.invoice_id.date_invoice,
                            'communication': 'BG/'+line.number,
                            'payment_method_id': rec.journal_id.outbound_payment_method_ids.id
                        }

                    statment_obj.create(vals)
                    statment_obj.post()
                    line.invoice_id.bg_paid = True
                    rec.state = 'paid'
            return statment_obj
