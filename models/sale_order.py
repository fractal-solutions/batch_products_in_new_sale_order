from odoo import models, fields
from odoo.exceptions import UserError
import base64
import csv
import io

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    csv_file = fields.Binary(string="Upload CSV")
    csv_filename = fields.Char(string="CSV Filename")

    def action_import_csv_products(self):
        for order in self:
            if not order.csv_file:
                continue

            try:
                data = base64.b64decode(order.csv_file)
                file_input = io.StringIO(data.decode("utf-8"))
                reader = csv.DictReader(file_input)
            except Exception as exc:
                raise UserError("Unable to read CSV file. Ensure it is UTF-8 encoded.") from exc

            row_errors = []
            imported_count = 0

            for row_index, row in enumerate(reader, start=2):
                default_code = (row.get('default_code') or '').strip()
                name = (row.get('name') or '').strip()
                quantity_raw = (row.get('quantity') or '1').strip()
                price_raw = (row.get('price') or '').strip()

                product = self.env['product.product'].search([
                    ('default_code', '=', default_code)
                ], limit=1) if default_code else self.env['product.product']

                if not product and name:
                    product = self.env['product.product'].search([
                        ('name', '=', name)
                    ], limit=1)

                if not product:
                    row_errors.append(
                        "Row %s: product not found (default_code='%s', name='%s')" % (
                            row_index, default_code or "-", name or "-"
                        )
                    )
                    continue

                try:
                    quantity = float(quantity_raw) if quantity_raw else 1.0
                    price_unit = float(price_raw) if price_raw else product.list_price
                except ValueError:
                    row_errors.append(
                        "Row %s: invalid quantity/price (quantity='%s', price='%s')" % (
                            row_index, quantity_raw or "-", price_raw or "-"
                        )
                    )
                    continue

                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': product.id,
                    'product_uom_qty': quantity,
                    'price_unit': price_unit,
                })
                imported_count += 1

            if row_errors:
                raise UserError(
                    "Batch import completed with errors.\n\n"
                    "Imported lines: %s\n"
                    "Failed lines: %s\n\n"
                    "Details:\n- %s" % (
                        imported_count,
                        len(row_errors),
                        "\n- ".join(row_errors)
                    )
                )
