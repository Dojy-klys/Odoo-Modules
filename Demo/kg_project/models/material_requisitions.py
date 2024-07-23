from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime


class MaterialPurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    def _get_buyer_domain(self):
        purchase_manager = self.env.ref('purchase.group_purchase_manager').users
        purchase_user = self.env.ref('purchase.group_purchase_user').users
        user_ids = []
        for usr in purchase_user:
            if usr.id not in purchase_manager.ids:
                user_ids.append(usr.id)
        return [('id', 'in', user_ids)]

    project_id = fields.Many2one('project.project')
    analytic_count = fields.Integer(string="Analytic Line", compute='compute_analytic_count', )
    bom_id = fields.Many2one('bom.selection')
    purchase_user_id = fields.Many2one('res.users', string='Purchase Representative', domain=_get_buyer_domain)
    show_decorations = fields.Boolean('Show Decorations', default=False)
    is_fully_available = fields.Boolean('Fully Available')
    purchase_order_count = fields.Integer('Purchase Order', compute='_get_purchase_order_count')
    is_rfq_needed = fields.Boolean('Is Rfq needed')

    # picking_count = fields.Integer(compute='_get_picking_count')

    def _get_purchase_order_count(self):
        for rec in self:
            po_ids = self.env['purchase.order'].search([]).filtered(
                lambda x: rec.id in x.requisition_po_id.ids)
            rec.purchase_order_count = len(po_ids)

    # def _get_picking_count(self):
    #     for rec in self:
    #         rec.picking_count = len(rec.picking_ids)

    # def compute_is_fully_available(self):
    #     for rec in self:
    #         rec.is_fully_available = False
    #         demand_qty = sum(rec.requisition_line_ids.mapped('qty'))
    #         stock_qty = sum(rec.requisition_line_ids.mapped('stock_qty'))
    #         print(rec.is_fully_available,'sdsdsdsdsd')
    #         if demand_qty >= stock_qty:
    #             rec.is_fully_available = True

    def compute_analytic_count(self):
        for record in self:
            record.analytic_count = False
            account_id = self.env['account.analytic.account'].search([('name', '=', self.project_id.name)])
            print(account_id, 'account_id')
            print(record.analytic_count, 'ddddddddddd')
            record.analytic_count = self.env['account.analytic.line'].search_count(
                [('account_id', '=', account_id.id), ('material_request_line_id', '=', self.id)])

    def action_get_analytic_record(self):
        self.ensure_one()
        account_id = self.env['account.analytic.account'].search([('name', '=', self.project_id.name)])
        print(account_id)
        # self.account_id = False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Analytic Line',
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.line',
            'domain': [('account_id', '=', account_id.id), ('material_request_line_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def purchase_order_button(self):
        self.ensure_one()
        po_ids = self.env['purchase.order'].search([]).filtered(
            lambda x: x.requisition_po_id.id == self.id or self.id in x.requisition_po_id.ids)
        return {
            'name': 'Purchase Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', po_ids.ids)],
        }

    # def action_get_picking_record(self):
    #     self.ensure_one()
    #     po_ids = self.picking_ids.ids
    #     return {
    #         'name': 'Transfers',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'stock.picking',
    #         'domain': [('id', 'in', po_ids)],
    #     }

    # @api.onchange('project_id')
    # def onchange_requisitions_line(self):
    #     for order in self:
    #         if order.project_id:
    #             analytic_pool = self.env['account.analytic.account']
    #             plan_id = self.env['account.analytic.plan'].search([('company_id', '=', order.company_id.id)], limit=1)
    #             if plan_id:
    #                 analytic_val = {'name': order.project_id.name, 'plan_id': plan_id.id}
    #             else:
    #                 raise UserError("Analytic account plan is not Configured for the logged in User's Company")
    #
    #             analytic = analytic_pool.search([('name', '=', order.project_id.name)])
    #             if not analytic:
    #                 analytic = analytic_pool.create(analytic_val)
    #
    #             for line in order.requisition_line_ids:
    #                 if not line.analytic_id:
    #                     line.analytic_id = analytic

    def action_done(self):
        res = super(MaterialPurchaseRequisition, self).action_done()
        if self.requisition_line_ids:
            for rec in self.requisition_line_ids:
                vals = {
                    'name': rec.description,
                    'account_id': rec.analytic_id.id,
                    'amount': rec.price_unit,
                    'date': self.requisition_date,
                    'unit_amount': rec.qty,
                    'product_id': rec.product_id.id,
                    'product_uom_id': rec.uom_id.id,
                    'material_request_line_id': self.id
                }
                self.env['account.analytic.line'].create(vals)

        return res

    def check_availability(self):
        # self.is_fully_available = False
        # self.is_rfq_needed = False
        self.show_decorations = True
        self.check_qunt()
        for rec in self.requisition_line_ids:

            stock_quant = self.env['stock.quant'].search(
                [('product_id', '=', rec.product_id.id), ('quantity', '>', 0),
                 ('location_id.usage', 'in', ['internal', 'transit'])])
            if stock_quant:
                rec.stock_qty = sum(stock_quant.mapped('quantity'))

            demand_qty = rec.qty
            stock_qty = rec.stock_qty
            rec.is_fully_available = False
            rec.is_rfq_needed = False
            rec.qty_needed_for_mr = stock_qty - demand_qty
            print(demand_qty, 'ssssssss')
            print(stock_qty, 'stock_qty')
            if demand_qty <= stock_qty:
                rec.is_fully_available = True
            else:
                rec.is_rfq_needed = True

    def check_qunt(self):
        rfq_not_need = self.requisition_line_ids.mapped('is_rfq_needed')
        is_fully_satisfied = self.requisition_line_ids.mapped('is_fully_available')
        self.is_fully_available = False
        self.is_rfq_needed = False
        print(rfq_not_need)
        print(is_fully_satisfied)
        if any(rfq_not_need):
            self.is_rfq_needed = True

        if all(is_fully_satisfied):
            self.is_fully_available = True

    def action_reset_draft(self):
        res = super(MaterialPurchaseRequisition, self).action_reset_draft()
        self.is_rfq_needed = False
        self.is_fully_available = False
        # self.is_fully_available = False

        return res

    def action_done(self):
        for requisition in self:
            requisition.check_qunt()
            if not requisition.is_dm_approve:
                raise UserError(_("Please get the Material Request Approved before Confirmation"))
            if not self.is_fully_available:
                raise UserError(_("Component's stock isn't satisfied"))
            internal = self.env.ref('kg_project.stock_picking_material_issue').id
            delivery_order = self.env['stock.picking'].create({
                'partner_id': self.employee_id.user_partner_id.id,
                'picking_type_id': internal,
                'mr_id': requisition.id

            })
            for line in requisition.requisition_line_ids:
                delivery_order_line = self.env['stock.move'].create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty,
                    'picking_id': delivery_order.id,
                    'location_id': self.picking_type_id.default_location_dest_id.id,
                    'location_dest_id': self.project_id.stock_location_id.id,
                })
            delivery_order.action_confirm()
            delivery_order.button_validate()
            requisition.picking_ids = [(4, delivery_order.id)]
            requisition.write({'state': 'done', 'completion_date': datetime.now()
                               })


class RequisitionLine(models.Model):
    _inherit = "requisition.line"

    analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account",
                                  compute='compute_analytic_account')
    delivery_date = fields.Date('Delivery Date')
    project_id = fields.Many2one('project.project', related='requisition_id.project_id')

    stock_qty = fields.Float('stock_qty')
    show_decorations = fields.Boolean('Show Decorations', related='requisition_id.show_decorations')
    ordered_qty = fields.Float(compute='compute_ordered_qty')
    is_fully_available = fields.Boolean('Fully Available')
    is_rfq_needed = fields.Boolean('Is Rfq needed')
    qty_needed_for_mr = fields.Float('Quantity Needed')

    # @api.depends('stock_qty','qty')
    # def compute_stock_needed(self):
    #     for rec in self:
    #         print(rec,'ddddddddddd')

    @api.depends('project_id')
    def compute_analytic_account(self):
        for order in self:
            order.analytic_id = False
            if order.project_id:
                analytic_pool = self.env['account.analytic.account']
                plan_id = self.env['account.analytic.plan'].search(
                    [('company_id', '=', order.requisition_id.company_id.id)], limit=1)
                if plan_id:
                    analytic_val = {'name': order.project_id.name, 'plan_id': plan_id.id,
                                    'material_request_line_id': order.requisition_id.id}
                else:
                    raise UserError("Analytic account plan is not Configured for the logged in User's Company")

                analytic = analytic_pool.search([('name', '=', order.project_id.name)])
                if not analytic:
                    analytic = analytic_pool.create(analytic_val)

                # for line in order.requisition_line_ids:
                if not order.analytic_id:
                    order.analytic_id = analytic

    def compute_ordered_qty(self):
        for rec in self:
            rec.ordered_qty = False
            po_ids = self.env['purchase.order'].search([]).filtered(
                lambda x: x.requisition_po_id.id == rec.requisition_id.id or rec.id in x.requisition_po_id.ids)
            print('po_ids', po_ids)
            # purchase = po_ids.order_line.mapped('product_qty')
            # print(purchase, 'qqqq')
            # rec.ordered_qty = purchase
        # def compute_stock_qty(self):
#     for rec in self:
#         rec.stock_qty = False
#         stock_quant = self.env['stock.quant'].search(
#             [('product_id', '=', rec.product_id.id), ('quantity', '>', 0),
#              ('location_id.usage', 'in', ['internal', 'transit'])])
#         if stock_quant:
#             rec.stock_qty = stock_quant.quantity
#         print(stock_quant.quantity, 'sssssssssssssssssss')
