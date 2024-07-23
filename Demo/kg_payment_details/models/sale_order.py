from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_amount = fields.Float(string='Invoice Amount', compute='_compute_invoice_amount')
    paid_amount = fields.Float(string='Paid Amount', compute='_compute_paid_amount')
    due_amount = fields.Float(string='Due Amount', compute='_compute_due_amount')



    def _compute_invoice_amount(self):
        for record in self:
            invoice_id = self.env['account.move'].search(
                ['&', ('invoice_origin', '=', record.name), '|', ('state', '=', 'draft'), ('state', '=', 'posted'),
                 ('payment_state', 'not in', ['reversed', 'invoicing_legacy'])])
            invoice = 0
            if invoice_id:
                invoice_amount = sum(inv.amount_total for inv in invoice_id)

            else:
                record.invoice_amount = invoice

    @api.depends('paid_amount', 'invoice_amount', 'due_amount')
    def _compute_due_amount(self):
        for record in self:
            invoice_ids = self.env['account.move'].search(
                ['&', ('invoice_origin', '=', record.name), '|', ('state', '=', 'draft'), ('state', '=', 'posted'),
                 ('payment_state', 'not in', ['reversed', 'invoicing_legacy'])])
            amount = 0

            if invoice_ids:
                for inv in invoice_ids:
                    amount += inv.amount_residual
                    record.due_amount = amount
            else:
                record.due_amount = amount

    @api.onchange('invoice_amount', 'due_amount')
    def _compute_paid_amount(self):
        self.paid_amount = float(self.invoice_amount) - float(self.due_amount)

