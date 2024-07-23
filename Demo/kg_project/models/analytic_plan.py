from odoo import fields, models


class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=False,
                                 default=lambda self: self.env.company)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    material_request_line_id = fields.Many2one(
        'material.purchase.requisition',
        string='Material Request Item',
        ondelete='cascade', related='account_id.material_request_line_id'
    )


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    material_request_line_id = fields.Many2one(
        'material.purchase.requisition',
        string='Material Request Item',
        ondelete='cascade',
    )
