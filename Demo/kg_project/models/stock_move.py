from odoo import fields, models, api
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange('product_uom_qty', 'quantity')
    def _check_demanded_qty(self):
        for move in self:
            if move.sale_line_id:
                if move.quantity > move.product_uom_qty:
                    raise ValidationError(
                        'The demanded quantity cannot exceed the ordered quantity for product: %s' % move.product_id.name
                    )
