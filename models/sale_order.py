from odoo import models, fields
from odoo.exceptions import UserError
import base64
import csv
import io

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    csv_file = fields.Binary(string="Upload CSV")

    def action_import_csv_products(self):
        for order in self:
            if not order.csv_file:
                continue

            # Decode CSV
            data = base64.b64decode(order.csv_file)
            file_input = io.StringIO(data.decode("utf-8"))
            reader = csv.DictReader(file_input)

            missing_products = []

            for row in reader:
                # Require product to exist by default_code or name
                product = self.env['product.product'].search([
                    ('default_code', '=', row.get('default_code'))
                ], limit=1)

                if not product:
                    product = self.env['product.product'].search([
                        ('name', '=', row.get('name'))
                    ], limit=1)

                if not product:
                    # Collect missing product info for warning
                    missing_products.append(row.get('default_code') or row.get('name'))
                    continue

                # Add product to order line
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': product.id,
                    'product_uom_qty': float(row.get('quantity', 1)),
                    'price_unit': float(row.get('price', product.list_price)),
                })

            # Raise error if any products were missing
            if missing_products:
                raise UserError(
                    "The following products were not found in Odoo:\n- " +
                    "\n- ".join(missing_products)
                )