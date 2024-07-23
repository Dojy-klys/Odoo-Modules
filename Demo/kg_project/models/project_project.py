from odoo import fields, models, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    bom_line_ids = fields.One2many('bom.line', 'project_id')
    is_bom_line_empty = fields.Boolean(string='Is BOM Line Empty', compute='_compute_is_bom_line_empty')
    sequence = fields.Char()
    bom_count = fields.Integer(compute='compute_bom_count')

    @api.depends('bom_line_ids')
    def _compute_is_bom_line_empty(self):
        for record in self:
            record.is_bom_line_empty = bool(record.bom_line_ids)

    def compute_bom_count(self):
        for rec in self:
            rec.bom_count = False
            rec.bom_count = self.env['bom.selection'].search_count([('project_id', '=', rec.id)])

    # def create_mr(self):
    #     vals = []
    #     for rec in self.bom_line_ids:
    #         vals.append((0, 0, {
    #             'product_id': rec.product_id.id,
    #             'description': rec.product_id.name,
    #             'qty': rec.qty,
    #         }))
    #     mr_id = self.env['material.purchase.requisition'].create({
    #         'department_res_id': 1,
    #         'project_id': self.id,
    #
    #         'requisition_line_ids': vals
    #     })
    #     return {
    #         'name': 'Material Request',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'material.purchase.requisition',
    #         'res_id': mr_id.id,
    #         'context': {'default_project_id': self.id}
    #     }

    def create_variation(self):
        sale_order = self.env['sale.order'].search([('project_id', '=', self.id)], limit=1, order='id DESC')
        print('sale', sale_order)
        print('sale', sale_order.name)
        return {
            'name': 'Variation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'context': {'default_project_type': 'existing', 'default_project_id': self.id,
                        'default_partner_id': self.partner_id.id, 'default_revision_id': sale_order.revision_id.id}
        }

    def action_view_bom(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Project',
            'view_mode': 'tree,form',
            'res_model': 'bom.selection',
            'context': "{'create':False}",
            'domain': [('project_id', '=', self.id)]
        }

    def create_bom(self):
        return {
            'name': 'Create BOM',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'bom.selection',
            'target': 'current',
            'context': {'default_project_id': self.id}
        }

    # def action_approve(self):
    #     self.create_mr()
    #
    def create_invoice_from_project(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("kg_project.action_view_project_invoice_wizard")
        action['context'] = {
            'default_project_id': self.id,

        }
        action['domain'] = [('project_id', '=', self.id)]
        return action


class ProjectBOMLines(models.Model):
    _name = 'bom.line'

    project_id = fields.Many2one('project.project')
    # bom_selection_id = fields.Many2one('bom.selection.line')
    product_category_id = fields.Many2one('product.category', 'Product category',
                                          )
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Quantity')
