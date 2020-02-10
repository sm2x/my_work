# -*- coding: utf-8 -*-
from datetime import datetime
from time import strptime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class OmmatMrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_qty = fields.Float(
        'Quantity', default=1.0, digits=(16, 4), required=True)


class OmmatMrpBom(models.Model):
    _inherit = 'mrp.bom'

    gender = fields.Selection(related='product_tmpl_id.gender', string='Gender')
    dynasty = fields.Many2one(related='product_tmpl_id.dynasty', string='Dynasty')
    week_no = fields.Integer('Week No', default='1')

    location_src_id = fields.Many2one(related='picking_type_id.default_location_src_id', string='Raw Material Location')
    src_lb_type = fields.Selection(related='location_src_id.type_l_b')
    src_fp_type = fields.Selection(related='location_src_id.type_f_p')

    location_dest_id = fields.Many2one(related='picking_type_id.default_location_dest_id',
                                       string='Finished Products Location')
    dest_lb_type = fields.Selection(related='location_dest_id.type_l_b')
    dest_fp_type = fields.Selection(related='location_dest_id.type_f_p')

    pro = fields.Boolean('Production')
    lab = fields.Boolean('Lab')

    labor_expense_account_id = fields.Many2one('account.account', 'Labor Expense Account',
                                               domain=[('deprecated', '=', False)], copy=False)
    product_deprecation_account_id = fields.Many2one('account.account', 'Product Deprecation Account',
                                                     domain=[('deprecated', '=', False)], copy=False)

    operation_expense_account_id = fields.Many2one('account.account', 'operation Expense Account',
                                                   domain=[('deprecated', '=', False)], copy=False)
    other_expense_account_id = fields.Many2one('account.account', 'Other Expense Account',
                                               domain=[('deprecated', '=', False)], copy=False)

    labor_expense_amount = fields.Float(string='Labor Expense', copy=False)
    operation_expense_amount = fields.Float(string='Operation Expense', copy=False)
    other_expense_amount = fields.Float(string='Other Expense', copy=False)

    @api.multi
    def action_mrp_production(self):
        mrp_obj = self.env['mrp.production']

        mrp_obj.create({
            'product_id': self.product_tmpl_id.product_variant_id.id,
            'product_qty': self.product_qty,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'bom_id': self.id,
            'picking_type_id': self.picking_type_id.id,
        })

    @api.constrains('product_id', 'product_tmpl_id', 'bom_line_ids')
    def _check_product_recursion(self):
        return False

    @api.multi
    @api.onchange('product_id', 'product_qty', 'sub_products')
    def compute_product_qty(self):
        for line in self.sub_products:
            if line.product_id.scrap:
                # self.product_qty = 3
                # print('outer')
                for bom_line in self.bom_line_ids:
                    if bom_line.product_id.id == line.product_id.id:
                        # print('inner if')
                        # print(bom_line.product_id.name)
                        # print(rec.bom_id.product_id.name)
                        line.product_qty = bom_line.product_qty-self.product_qty


class OmmatMrpProduction(models.Model):
    _inherit = 'mrp.production'

    subproduct_ids = fields.One2many('mrp.subproduct', 'mrp_id', related='bom_id.sub_products', readonly=False)

    dynasty = fields.Many2one(related='product_id.dynasty', string='Dynasty')
    gender = fields.Selection(related='bom_id.gender', string='Gender')
    week_no = fields.Integer('Week No', store=True)
    pro = fields.Boolean(related='bom_id.pro', string='Production')
    lab = fields.Boolean(related='bom_id.lab', string='Lab')

    loc = fields.Many2one('stock.quant', compute='get_dy_products')

    product_id_f = fields.Many2one('product.template', string='الصنف -انثى', compute='get_dy_products')
    product_qty_f = fields.Float('Quantity', compute='get_dy_products')
    product_cost_f = fields.Float('Cost', compute='get_dy_products')

    product_id_fm = fields.Many2one('product.template', string='الصنف -انثى منتج', compute='get_dy_products')
    product_qty_fm = fields.Float('Quantity', compute='get_dy_products')
    product_cost_fm = fields.Float('Cost', compute='get_dy_products')

    product_id_m = fields.Many2one('product.template', string='الصنف -ذكر', compute='get_dy_products')
    product_qty_m = fields.Float('Quantity', compute='get_dy_products')
    product_cost_m = fields.Float('Cost', compute='get_dy_products')

    journal_id = fields.Many2one('account.journal', string='Journal', compute='get_dy_products')
    e_value_acc_debit = fields.Many2one('account.account', string='حساب مدين', compute='get_dy_products')
    e_value_acc_credit = fields.Many2one('account.account', string='حساب دائن', compute='get_dy_products')

    production_per = fields.Float('Production Percentage', compute='get_dy_products', digits=(16, 10))
    ommat_dep = fields.Float('depreciation', compute='get_dy_products'
                             , help='number of ommat will depreciation , عدد الامهات اللي سوف تهلك')
    dep_value = fields.Float('Depreciation Amount', compute='get_dy_products', digits=(16, 4)
                             ,
                             help='Depreciation value for this MO = number of Ommat will depreciate * cost for one omma , قيمة الاهلاك')

    e_value = fields.Float('Catalog Estimated sales value ', compute='get_e_value', digits=(16, 4)
                           , help='from Catalog estimated sales amount , القيمة البيعية المقدرة')
    e_value_per_mo = fields.Float('MO Estimated sales value', compute='get_e_value', digits=(16, 4)
                                  , help='estimated sales amount , القيمة البيعية المقدرة')

    clicked = fields.Boolean(copy=False)

    product_deprecation_amount = fields.Float(string='Product Deprecation', copy=False, compute='get_dy_products')

    @api.multi
    def create_other_expense(self):
        # catalogue = self.env['ommat.catalogue'].search(
        #     [('dynasty', '=', self.dynasty.id), ('state', '=', 'in_progress')])
        #
        # journal_id = catalogue.journal_id
        # self.env['account.journal'].search([('name', '=', 'Stock Journal')], limit=1)
        journal_id = self.env['account.journal'].search([('type', '=', 'general')], limit=1)

        if not journal_id:
            raise ValueError(_('Please add Catalogue Journal'))

        if self.bom_id.other_expense_account_id and self.other_expense_amount > 0:
            product_categ = self.product_id.categ_id
            other_expense_move = self.env['account.move'].create({

                'journal_id': journal_id.id,
                'date': datetime.today(),
                'ref': "Other Expence "+str(self.name),

            })

            other_expense_move_one = self.env['account.move.line'].with_context(check_move_validity=False).create({

                'move_id': other_expense_move.id,
                'account_id': self.bom_id.other_expense_account_id.id,
                'product_id': self.product_id.id,
                # 'product_uom_id': self.product_uom_id.id,
                # 'quantity': self.product_qty,
                'name': "Other Expence "+str(self.product_id.name),
                'debit': 0,
                'credit': self.bom_id.other_expense_amount, })

            labor_move_two = self.env['account.move.line'].with_context(check_move_validity=False).create({

                'move_id': other_expense_move.id,
                'account_id': product_categ.property_stock_valuation_account_id.id,
                'product_id': self.product_id.id,
                # 'product_uom_id': self.product_uom_id.id,
                # 'quantity': self.product_qty,
                'name': "Other expense on "+str(self.product_id.name),
                'debit': self.bom_id.other_expense_amount,
                'credit': 0})
            if other_expense_move:
                other_expense_move.post()
                if self.move_finished_ids:
                    for move in self.move_finished_ids:
                        move.value += self.other_expense_amount
                        move.remaining_value = move.value

    @api.multi
    def create_operation_expense(self):
        # catalogue = self.env['ommat.catalogue'].search(
        #     [('dynasty', '=', self.dynasty.id), ('state', '=', 'in_progress')])
        #
        # journal_id = catalogue.journal_id
        journal_id = self.env['account.journal'].search([('type', '=', 'general')], limit=1)

        # journal_id = self.env['account.journal'].search([('name', '=', 'Stock Journal')], limit=1)
        if not journal_id:
            raise ValueError(_('Please add Catalogue Journal'))

        if self.bom_id.operation_expense_account_id and self.operation_expense_amount > 0:
            product_categ = self.product_id.categ_id
            operation_move = self.env['account.move'].create({

                'journal_id': journal_id.id,
                'date': datetime.today(),
                'ref': "operation Expence "+str(self.name),

            })

            operation_move_one = self.env['account.move.line'].with_context(check_move_validity=False).create({

                'move_id': operation_move.id,
                'account_id': self.bom_id.operation_expense_account_id.id,
                'product_id': self.product_id.id,
                # 'product_uom_id': self.product_uom_id.id,
                # 'quantity': self.product_qty,
                'name': "operation Expence "+str(self.product_id.name),
                'debit': 0,
                'credit': self.bom_id.operation_expense_amount, })

            labor_move_two = self.env['account.move.line'].with_context(check_move_validity=False).create({

                'move_id': operation_move.id,
                'account_id': product_categ.property_stock_valuation_account_id.id,
                'product_id': self.product_id.id,
                # 'product_uom_id': self.product_uom_id.id,
                # 'quantity': self.product_qty,
                'name': "operation on "+str(self.product_id.name),
                'debit': self.bom_id.operation_expense_amount,
                'credit': 0})
            if operation_move:
                operation_move.post()
                if self.move_finished_ids:
                    for move in self.move_finished_ids:
                        move.value += self.bom_id.operation_expense_amount
                        move.remaining_value = move.value

    @api.multi
    def create_labor_expence(self):
        # catalogue = self.env['ommat.catalogue'].search(
        #     [('dynasty', '=', self.dynasty.id), ('state', '=', 'in_progress')])
        #
        # journal_id = catalogue.journal_id
        journal_id = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        # journal_id=self.env['account.journal'].search([('name','=','Stock Journal')],limit=1)

        if not journal_id:
            raise ValueError(_('Please add Catalogue Journal'))

        if self.bom_id.labor_expense_account_id and self.labor_expense_amount > 0:
            product_categ = self.product_id.categ_id
            labor_move = self.env['account.move'].create({

                'journal_id': journal_id.id,
                'date': datetime.today(),
                'ref': "labor Expence "+str(self.name),

            })

            labor_move_one = self.env['account.move.line'].with_context(check_move_validity=False).create({

                'move_id': labor_move.id,
                'account_id': self.bom_id.labor_expense_account_id.id,
                'product_id': self.product_id.id,
                # 'product_uom_id': self.product_uom_id.id,
                # 'quantity': self.product_qty,
                'name': "labor Expence "+str(self.product_id.name),
                'debit': 0,
                'credit': self.bom_id.labor_expense_amount, })

            labor_move_two = self.env['account.move.line'].with_context(check_move_validity=False).create({

                'move_id': labor_move.id,
                'account_id': product_categ.property_stock_valuation_account_id.id,
                'product_id': self.product_id.id,
                # 'product_uom_id': self.product_uom_id.id,
                # 'quantity': self.product_qty,
                'name': "labor Expence on "+str(self.product_id.name),
                'debit': self.bom_id.labor_expense_amount,
                'credit': 0})
            if labor_move:
                labor_move.post()
                if self.move_finished_ids:
                    for move in self.move_finished_ids:
                        move.value += self.bom_id.labor_expense_amount
                        move.remaining_value = move.value

    @api.multi
    def create_product_deprecation(self):
        catalogue = self.env['ommat.catalogue'].search(
            [('dynasty', '=', self.dynasty.id), ('state', '=', 'in_progress')])
        #
        # journal_id = catalogue.journal_id
        # # journal_id = self.env['account.journal'].search([('name', '=', 'Stock Journal')], limit=1)
        #
        journal_id = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        if not journal_id:
            raise ValueError(_('Please add Catalogue Journal'))

        if self.product_deprecation_amount > 0:
            product_categ = self.product_id.categ_id
            product_deprecation_move = self.env['account.move'].create({

                'journal_id': journal_id.id,
                'date': datetime.today(),
                'ref': "Product deprecation"+str(self.name),

            })

            product_deprecation_move_one = self.env['account.move.line'].with_context(check_move_validity=False).create(
                {

                    'move_id': product_deprecation_move.id,
                    'account_id': catalogue.depreciation_account.id,
                    'product_id': self.product_id.id,
                    # 'product_uom_id': self.product_uom_id.id,
                    # 'quantity': self.product_qty,
                    'name': "Product deprecation"+str(self.product_id.name),
                    'debit': 0,
                    'credit': self.product_deprecation_amount, })

            product_deprecation_move_two = self.env['account.move.line'].with_context(check_move_validity=False).create(
                {

                    'move_id': product_deprecation_move.id,
                    'account_id': product_categ.property_stock_valuation_account_id.id,
                    'product_id': self.product_id.id,
                    # 'product_uom_id': self.product_uom_id.id,
                    # 'quantity': self.product_qty,
                    'name': "Product deprecation"+str(self.product_id.name),
                    'debit': self.product_deprecation_amount,
                    'credit': 0})
            if product_deprecation_move:
                product_deprecation_move.post()
                if self.move_finished_ids:
                    for move in self.move_finished_ids:
                        move.value += self.product_deprecation_amount
                        move.remaining_value = move.value

    @api.multi
    def button_mark_done(self):
        rec = super(OmmatMrpProduction, self).button_mark_done()
        self.create_labor_expence()
        self.create_operation_expense()
        self.create_other_expense()
        self.create_product_deprecation()

        return rec

    @api.multi
    def get_dy_products(self):
        self.ensure_one()
        catalogue = self.env['ommat.catalogue'].search(
            [('dynasty', '=', self.dynasty.id), ('state', '=', 'in_progress')])
        # x = self.product_id_f.product_variant_id.qty_at_date
        # self.product_cost_m = self.product_id_m.product_variant_id.stock_value / z

        # z = self.product_id_m.product_variant_id.qty_at_date

        if catalogue:

            self.e_value_acc_credit = catalogue.e_value_acc_credit
            self.e_value_acc_debit = catalogue.e_value_acc_debit
            self.journal_id = catalogue.journal_id

            self.product_id_f = catalogue.product_id_f
            self.product_id_fm = catalogue.product_id_fm
            self.product_id_m = catalogue.product_id_m
            y = self.product_id_fm.product_variant_id.qty_at_date

            if y:
                print('y =', y)
                # self.product_qty_f = self.env['stock.quant'].search([('location_id', '=', self.location_src_id.id), (
                #     'product_tmpl_id', '=', self.product_id_f.id)]).quantity
                # self.product_cost_f = self.product_id_f.product_variant_id.stock_value / x

                self.product_qty_fm = self.env['stock.quant'].search([('location_id', '=', self.location_src_id.id), (
                    'product_tmpl_id', '=', self.product_id_fm.id)]).quantity
                self.product_cost_fm = self.product_id_fm.product_variant_id.stock_value / y

                self.production_per = (self.product_qty / self.product_qty_fm) / 100
                self.ommat_dep = self.production_per * self.product_qty_fm
                self.dep_value = self.ommat_dep * self.product_cost_fm

                # self.product_qty_m = self.env['stock.quant'].search([('location_id', '=', self.location_src_id.id), (
                #     'product_tmpl_id', '=', self.product_id_m.id)]).quantity

                if self.pro:
                    self.product_deprecation_amount = self.dep_value

    @api.one
    def get_e_value(self):
        self.ensure_one()
        catalogue = self.env['ommat.catalogue'].search(
            [('dynasty', '=', self.dynasty.id), ('state', '=', 'in_progress')])

        if self.location_src_id.type_l_b == 'land':
            self.e_value = catalogue.e_value_l
        else:
            self.e_value = catalogue.e_value_b

        self.e_value_per_mo = self.e_value * self.production_per

    @api.multi
    def create_journal(self):
        company = self.env.user.company_id
        account_move = self.env['account.move']
        if not self.journal_id:
            raise ValueError(_('please create Stock Journal'))

        if not (self.e_value_acc_debit and self.e_value_acc_debit):
            raise ValueError(_('please check Accounts'))

        line_ids = [
            (0, 0,
             {'journal_id': self.journal_id.id,
              'account_id': self.e_value_acc_debit.id,
              'name': self.name,
              # 'amount_currency': -cheque_obj.amount_currency or False,
              'currency_id': company.currency_id.id,
              'debit': self.e_value_per_mo}),

            (0, 0, {'journal_id': self.journal_id.id,
                    'account_id': self.e_value_acc_credit.id,
                    # 'partner_id': cheque_obj.partner_id.id,
                    'name': self.name,
                    # 'amount_currency': cheque_obj.amount_currency or False,
                    'currency_id': company.currency_id.id,
                    'credit': self.e_value_per_mo})
        ]
        vals = {
            'journal_id': self.journal_id.id,
            'ref': self.name,
            'date': self.date_planned_start,
            'line_ids': line_ids,
        }
        account_move.create(vals)
        self.clicked = True


class OmmatMrpSubProduct(models.Model):
    _inherit = 'mrp.subproduct'

    mrp_id = fields.Many2one('mrp.production', compute='get_mrp')

    gender = fields.Selection(related='bom_id.gender', string='Gender')
    dynasty = fields.Many2one(related='bom_id.dynasty', string='Dynasty')
    week_no = fields.Integer(related='mrp_id.week_no', string='Week No', requierd=True, store=True)
    loc_type = fields.Selection(related='mrp_id.location_dest_id.type_l_b', string='Src Type')
    state = fields.Selection(related='mrp_id.state', string='State')
    reason = fields.Selection([('r1', 'Scrap'),
                               ('r2', 'Execute'),
                               ('r3', 'Employee consumable'),
                               ('r4', 'Other')
                               ], copy=False, requierd=True)

    @api.multi
    def get_mrp(self):
        for rec in self:
            mrb_objs = rec.env['mrp.production'].search([('bom_id', '=', rec.bom_id.id)])
            for obj in mrb_objs:
                rec.mrp_id = obj.id


class OmmatStockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    gender = fields.Selection(related='product_id.gender', string='Gender')
    dynasty = fields.Many2one(related='product_id.dynasty', string='Dynasty')
    week_no = fields.Integer(related='move_id.production_id.week_no', string='Week No', requierd=True, store=True)
    loc_type = fields.Selection(related='move_id.production_id.location_dest_id.type_l_b', string='Src Type')
    mrp_state = fields.Selection(related='move_id.production_id.state', string='State')


class OmmatProduct(models.Model):
    _inherit = ['product.template']

    scrap = fields.Boolean('Scrap')
    dynasty = fields.Many2one('dynasty.model', string='Dynasty')

    gender = fields.Selection([('female', 'Female'),
                               ('male', 'Male')], copy=False)

    feed_type = fields.Selection([('feed', 'Feed'),
                                  ('med', 'Medical')], copy=False)


class OmmatStockMove(models.Model):
    _inherit = 'stock.move'

    gender = fields.Selection(related='raw_material_production_id.bom_id.gender', string='Gender')
    dynasty = fields.Many2one(related='raw_material_production_id.bom_id.dynasty', string='Dynasty')
    week_no = fields.Integer(related='raw_material_production_id.week_no', string='Week No', store=True)
    loc_type = fields.Selection(related='raw_material_production_id.location_dest_id.type_l_b',
                                string='Src Type')
    mrp_state = fields.Selection(related='raw_material_production_id.state', string='State', store=True)


class OmaatMrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    product_qty_onhand = fields.Float(string='Quantity On Hand',
                                      compute='_get_qty_onhand')

    @api.depends('product_id')
    def _get_qty_onhand(self):
        stock = self.env['stock.quant'].search(
            [('product_id', '=', self.product_id.id), ('location_id', '=', self.production_id.location_src_id.id)])
        self.product_qty_onhand = stock.quantity


class OmaatMrpProductProduceupdate(models.TransientModel):
    _inherit = "change.production.qty"

    product_qty_onhand = fields.Float(string='Quantity On Hand',
                                      compute='_get_qty_onhand')

    @api.depends('mo_id')
    def _get_qty_onhand(self):
        stock = self.env['stock.quant'].search(
            [('product_id', '=', self.mo_id.product_id.id), ('location_id', '=', self.mo_id.location_src_id.id)])
        self.product_qty_onhand = stock.quantity
