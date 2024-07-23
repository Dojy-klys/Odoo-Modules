from odoo import fields, models, api
from odoo.exceptions import ValidationError


class BOMSelection(models.Model):
    _name = 'bom.selection'

    name = fields.Char(string='Name', copy=False, readonly=True, default='New')

    @api.model
    def create(self, values):
        if values.get('name', 'New') == 'New':
            values['name'] = self.env['ir.sequence'].next_by_code('bom.seq') or 'New'
        return super(BOMSelection, self).create(values)

    project_id = fields.Many2one('project.project')
    sale_order_ids = fields.Many2many('sale.order', compute='compute_sale_order',
                                      )
    sale_order_id = fields.Many2one('sale.order', domain="[('id', 'in', sale_order_ids)]")
    bom_selection_ids = fields.One2many('bom.selection.line', 'bom_selection_id',
                                        ondelete='cascade', compute='compute_bom_selection', store=True)
    product_ids = fields.Many2many('product.product', compute='compute_product_ids')
    product_category_ids = fields.Many2many('product.category', compute='compute_product_ids')
    product_id = fields.Many2one('product.product', 'Cabinet Product', domain="[('id', 'in', product_ids)]")
    product_category_id = fields.Many2one('product.category', 'Product category',
                                          domain="[('id', 'in', product_category_ids)]")
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('approve', 'Approved'), ('reject', 'Rejected'),
                                        ('cancel', 'Cancel')], default='draft')
    mr_count = fields.Integer(compute='compute_mr_count', copy=False)
    show_bom_in = fields.Selection(selection=[('product', 'Product'), ('bom', 'BOM Category')], default='product')
    bom_category_id = fields.Many2one('bom.category', copy=False)
    qty = fields.Float('Quantity', default=1)

    @api.onchange('show_bom_in')
    def onchange_show_bom_in(self):
        if self.show_bom_in == 'bom':
            self.product_id = False
            self.product_category_id = False

    def compute_mr_count(self):
        for rec in self:
            rec.mr_count = False
            rec.mr_count = self.env['material.purchase.requisition'].search_count([('bom_id', '=', rec.id)])

    # @api.onchange('sale_order_id')
    # def onchange_product_id(self):
    #     res = []
    #     for rec in self.product_ids:
    #         res.append(rec._origin.id)
    #     return {'domain': {'product_id': [('id', 'in', res)]}}

    @api.depends('project_id')
    def compute_sale_order(self):
        for rec in self:
            rec.sale_order_ids = False
            if rec.project_id:
                rec.sale_order_ids = self.env['sale.order'].search([('project_id', '=', rec.project_id.id),('state','in',['sale','done'])]).ids
                print(rec.sale_order_ids, 'ddddddddddddddddd')
                if not (len(rec.sale_order_ids) > 1):
                    rec.sale_order_id = rec.sale_order_ids._origin

    @api.depends('sale_order_id', 'bom_category_id', 'show_bom_in')
    def compute_product_ids(self):
        for rec in self:
            rec.product_ids = False
            rec.product_id = False
            rec.product_category_ids = False
            if rec.sale_order_id:
                if rec.show_bom_in == 'product':
                    rec.product_ids = rec.sale_order_id.order_line.mapped('product_id').mapped('id')
                    rec.product_category_ids = rec.sale_order_id.order_line.mapped('product_id').mapped(
                        'categ_id').mapped('id')
                    if not (len(rec.product_ids) > 1):
                        rec.product_id = rec.product_ids.id

    # @api.model
    # def create(self, values):
    #     if values.get('name', 'New') == 'New':
    #         values['name'] = self.env['ir.sequence'].next_by_code('bom.seq') or 'New'
    #     return super(BOMSelection, self).create(values)

    # @api.onchange('sale_order_id','product_id', 'product_category_id', 'qty', 'show_bom_in', 'bom_category_id')
    # @api.depends('product_id', 'product_category_id', 'qty', 'show_bom_in', 'bom_category_id')
    # def compute_bom_selection(self):
    #     for rec in self:
    #         rec.bom_selection_ids = False
    #         rec.bom_selection_ids = [(5, 0, 0)]
    #         vals = []
    #         domain = []
    #
    #         if rec.show_bom_in == 'product' and rec.product_id:
    #             domain = [('product_id', '=', rec.product_id._origin.id)]
    #             if rec.product_category_id:
    #                 domain.append(('category_ids', '=', rec.product_category_id.id))
    #         elif rec.show_bom_in != 'product' and rec.bom_category_id:
    #             domain = [('bom_category_id', '=', rec.bom_category_id._origin.id)]
    #
    #         if domain:
    #             bom_ids = self.env['bom.master'].search(domain)
    #             for bom in bom_ids:
    #                 bom_line_ids = bom.bom_line_ids
    #                 if rec.show_bom_in == 'product' and rec.product_category_id:
    #                     bom_line_ids = bom_line_ids.filtered(
    #                         lambda
    #                             x: x.product_id.categ_id.id == rec.product_category_id.id or x.name == rec.product_category_id.name
    #                     )
    #                 for bom_line in bom_line_ids:
    #                     vals.append((0, 0, {
    #                         'display_type': bom_line.display_type,
    #                         'name': bom_line.name,
    #                         'product_id': bom_line.product_id.id if bom_line.product_id else False,
    #                         'qty': rec.qty * bom_line.qty if bom_line.display_type != 'line_section' else 1,
    #                         'bom_selection_id': rec.id
    #                     }))
    #
    #         rec.bom_selection_ids = vals

    @api.onchange('qty')
    def onchange_qty(self):
        qty = self.qty
        print('qty')
        bom_line = self.bom_selection_ids
        if bom_line:
            bom_line = bom_line.filtered(lambda x: x.display_type != 'line_section')
        for rec in bom_line:
            rec.write({'qty': qty * rec.bom_qty})
            # rec.qty = qty * rec.bom_qty

    @api.depends('product_id', 'product_category_id', 'show_bom_in', 'bom_category_id')
    def compute_bom_selection(self):
        for rec in self:
            rec.bom_selection_ids = [(5, 0, 0)]  # Clear existing one2many records
            vals = []
            domain = []
            rec.bom_selection_ids = False
            if rec.show_bom_in == 'product' and rec.product_id:
                domain = [('product_id', '=', rec.product_id._origin.id)]
                if rec.product_category_id:
                    domain.append(('category_ids', '=', rec.product_category_id.id))

                bom_ids = self.env['bom.master'].search(domain)
                for bom in bom_ids:
                    bom_line_ids = bom.bom_line_ids
                    if rec.show_bom_in == 'product' and rec.product_category_id:
                        bom_line_ids = bom_line_ids.filtered(
                            lambda
                                x: x.product_id.categ_id.id == rec.product_category_id.id or x.name == rec.product_category_id.name
                        )
                    for bom_line in bom_line_ids:
                        vals.append((0, 0, {
                            'display_type': bom_line.display_type,
                            'name': bom_line.name,
                            'product_id': bom_line.product_id.id if bom_line.product_id else False,
                            'qty': rec.qty * bom_line.qty if bom_line.display_type != 'line_section' else 1,
                            'bom_qty': bom_line.qty,
                            'bom_selection_id': rec.id
                        }))
                rec.bom_selection_ids = vals

            elif rec.show_bom_in != 'product' and rec.bom_category_id:
                domain = [('bom_category_id', '=', rec.bom_category_id._origin.id)]

                # if domain:
                bom_ids = self.env['bom.master'].search(domain)
                for bom in bom_ids:
                    bom_line_ids = bom.bom_line_ids
                    if rec.show_bom_in == 'product' and rec.product_category_id:
                        bom_line_ids = bom_line_ids.filtered(
                            lambda
                                x: x.product_id.categ_id.id == rec.product_category_id.id or x.name == rec.product_category_id.name
                        )
                    for bom_line in bom_line_ids:
                        vals.append((0, 0, {
                            'display_type': bom_line.display_type,
                            'name': bom_line.name,
                            'product_id': bom_line.product_id.id if bom_line.product_id else False,
                            'qty': rec.qty * bom_line.qty if bom_line.display_type != 'line_section' else 1,
                            'bom_qty': bom_line.qty,
                            'bom_selection_id': rec.id
                        }))

                rec.bom_selection_ids = vals

    def action_confirm(self):
        for rec in self:
            if not rec.bom_selection_ids:
                raise ValidationError('You need to List the components')
            rec.state = 'confirm'

    def action_approved(self):
        for rec in self:
            rec.state = 'approve'

    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_reset_to_draft(self):
        for rec in self:
            mr_ids = self.env['material.purchase.requisition'].search([('bom_id', '=', rec.id)])
            print(mr_ids, 'Mr')
            for mr in mr_ids:
                mr.action_cancel()
                mr.unlink()
            rec.state = 'draft'

    def create_mr(self):
        vals = []
        print('ssssssssssssssss')
        bom_lines = self.bom_selection_ids
        if bom_lines:
            bom_lines = bom_lines.filtered(lambda x: x.display_type == False and x.qty > 0)
        for rec in bom_lines:
            vals.append((0, 0, {
                'product_id': rec.product_id.id,
                'description': rec.product_id.name,
                'qty': rec.qty,
                # 'bom_qty': rec.qty,

                'uom_id': rec.product_id.uom_po_id.id
            }))
        mr_id = self.env['material.purchase.requisition'].create({
            'department_res_id': 1,
            'project_id': self.project_id.id,
            'bom_id': self.id,
            'requisition_line_ids': vals,
            'issue_location': self.project_id.stock_location_id.id
        })
        return {
            'name': 'Material Request',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'material.purchase.requisition',
            'res_id': mr_id.id,
            'context': {'default_project_id': self.project_id.id}
        }

    # def action_load_bom_lines(self):
    #     vals = []
    #     for rec in self.bom_selection_ids:
    #         vals.append((0, 0, {
    #             'product_category_id': rec.product_category_id.id,
    #             'product_id': rec.product_id.id,
    #             'qty': rec.qty,
    #
    #         }))
    #     self.project_id.write({
    #         'bom_line_ids': vals
    #     })
    #

    def action_view_mr(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Material Request',
            'view_mode': 'tree,form',
            'res_model': 'material.purchase.requisition',
            'context': "{'create':False}",
            'domain': [('bom_id', '=', self.id)]
        }


class BOMSelectionLine(models.Model):
    _name = 'bom.selection.line'

    bom_selection_id = fields.Many2one('bom.selection')
    product_category_id = fields.Many2one('product.category', 'Product category',
                                          related='bom_selection_id.product_category_id')
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Quantity', default=1)
    project_id = fields.Many2one('project.project', related='bom_selection_id.project_id')
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    name = fields.Char('Category')
    bom_qty = fields.Float('Quantity', default=1)
