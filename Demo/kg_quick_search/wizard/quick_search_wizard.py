from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date


class QuickSearchWizard(models.Model):
    _name = 'quick.search.wizard'

    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    quick_search_line_ids = fields.One2many('quick.search.sale.lines', 'quick_search_line_id',
                                            string="Quick Search Sales Line", readonly=True)

    is_purchase = fields.Boolean(string="Purchase")
    vendor_id = fields.Many2one('res.partner', string="Vendor", required=True)
    quick_search_purchase_ids = fields.One2many('quick.search.purchase.lines', 'quick_search_purchase_id',
                                                string="Quick Search Purchase Line", readonly=True)

    product_quantity_ids = fields.One2many('product.quantity.lines', 'product_quantity_id',
                                           string="Quick Search Purchase Line", readonly=True)


    @api.onchange('product_id', 'location')
    def onchange_product_quantity(self):
        self.product_quantity_ids = False
        quantity_data = []
        loc = self.env['stock.quant'].search([('product_id', '=', self.product_id.id)])
        for rec in loc:
            if rec.location_id.usage == 'internal':
                quantity_data.append(
                    (0, 0, {'product_id': rec.product_id, 'onhand_qty': rec.quantity, 'location': rec.location_id}))
        self.product_quantity_ids = quantity_data

    @api.onchange('partner_id', 'vendor_id', 'product_id', 'order_id.date_order', 'date_from', 'date_to')
    def onchange_partner_id(self):
        domain = []
        batch_lines = []
        self.quick_search_line_ids = False
        if self.is_purchase == False:
            if self.partner_id or self.product_id:
                if self.partner_id:
                    domain.append(('order_id.partner_id', '=', self.partner_id.id))
                if self.product_id:
                    domain.append(('product_id', '=', self.product_id.id))
                if self.date_from:
                    domain.append(('order_id.date_order', '>=', self.date_from))
                if self.date_to:
                    domain.append(('order_id.date_order', '<=', self.date_to))

                search_line = self.env['sale.order.line'].search(domain)
                for rec in search_line:
                    batch_lines.append((0, 0, {"sale_order_id": rec.order_id.id,
                                               "order_date": rec.order_id.date_order,
                                               "partner_id": rec.order_id.partner_id,
                                               "lpo": rec.order_id.client_order_ref,
                                               "ordered_qty": rec.product_uom_qty,
                                               "delivered_qty": rec.qty_delivered,
                                               "unit_price": rec.price_unit,
                                               "total": rec.price_subtotal,
                                               }))
                self.quick_search_line_ids = batch_lines

        else:
            domain = []
            batch_lines = []
            self.quick_search_purchase_ids = False
            if self.vendor_id or self.product_id:
                if self.vendor_id:
                    domain.append(('order_id.partner_id', '=', self.vendor_id.id))
                if self.product_id:
                    domain.append(('product_id', '=', self.product_id.id))
                if self.date_from:
                    domain.append(('order_id.date_order', '>=', self.date_from))
                if self.date_to:
                    domain.append(('order_id.date_order', '<=', self.date_to))
                search_line = self.env['purchase.order.line'].search(domain)
                for rec in search_line:
                    batch_lines.append((0, 0, {"purchase_order_id": rec.order_id.id,
                                               "product_id": rec.product_id,
                                               "quantity": rec.product_qty,
                                               "expected_arrival": rec.date_planned,
                                               "received_qty": rec.qty_received,
                                               "billed_qty": rec.qty_invoiced,
                                               "unit_price": rec.price_unit,
                                               "total": rec.price_subtotal,
                                               }))
                self.quick_search_purchase_ids = batch_lines


class QuickSearchSaleLines(models.Model):
    _name = 'quick.search.sale.lines'

    order_date = fields.Datetime(string="Order Date")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    lpo = fields.Char(string="LPO")
    partner_id = fields.Many2one('res.partner', string="Customer")
    ordered_qty = fields.Float(string="Ordered qty")
    delivered_qty = fields.Float(string="Delivered Qty")
    balance_qty = fields.Float(string="Balance Qty")
    unit_price = fields.Float(string="Unit Price")
    total = fields.Float(string="Total")

    quick_search_line_id = fields.Many2one('quick.search.wizard', string="Quick Search Line")


class QuickSearchPurchaseLines(models.Model):
    _name = 'quick.search.purchase.lines'

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float(string="Quantity")
    expected_arrival = fields.Datetime(string="Expected Arrival")
    received_qty = fields.Float(string="Received Qty")
    billed_qty = fields.Float(string="Billed Qty")
    unit_price = fields.Float(string="Unit Price")
    total = fields.Float(string="Total")
    vendors_id = fields.Many2one(string="Vendor", related="quick_search_purchase_id.vendor_id")

    quick_search_purchase_id = fields.Many2one('quick.search.wizard', string="Quick Search Purchase Line")


class ProductOnhandQuanity(models.Model):
    _name = 'product.quantity.lines'

    product_id = fields.Many2one('product.product', string="Product", related="product_quantity_id.product_id")
    onhand_qty = fields.Integer(string="Onhand Quantity")
    location = fields.Many2one('stock.location', string="Location", readonly=True)

    product_quantity_id = fields.Many2one('quick.search.wizard', string="Onhand Quantity line")
