# -*- coding: utf-8 -*-
"""
    sale_shipment_cost_cap.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from decimal import Decimal

from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction
from trytond.model import fields
from trytond.pyson import Eval


__all__ = ['Sale', 'Configuration']
__metaclass__ = PoolMeta


class Configuration:
    __name__ = 'sale.configuration'

    @classmethod
    def __setup__(cls):
        super(Configuration, cls).__setup__()

        method = ('shipment_capped', 'On Shipment (capped to Order total)')

        if method not in cls.sale_shipment_cost_method.selection:
            cls.sale_shipment_cost_method.selection.append(method)


class Sale:
    __name__ = 'sale.sale'

    shipment_amount = fields.Function(
        fields.Numeric(
            'Shipment Amount',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']
        ), 'get_shipment_amount'
    )
    shipment_amount_invoiced = fields.Function(
        fields.Numeric(
            'Shipment Amount Invoiced',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']
        ), 'get_shipment_amount'
    )

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()

        method = ('shipment_capped', 'On Shipment (capped to Order total)')

        if method not in cls.shipment_cost_method.selection:
            cls.shipment_cost_method.selection.append(method)

    def get_shipment_amount(self, name):
        """
        Return function field values
        """
        _zero = Decimal('0')

        if name == 'shipment_amount':
            return self.currency.round(
                sum(
                    map(lambda line: line.shipment_cost or _zero, self.lines)
                )
            )
        if name == 'shipment_amount_invoiced':
            result = _zero
            for shipment in self.shipments:
                if not shipment.cost_invoice_line:
                    continue
                result += shipment.cost_invoice_line.amount
            return self.currency.round(result)

    def _get_invoice_line_sale_line(self, invoice_type):
        """
        Delete the invoice line that would be normally created for the sale
        if the shipment_cost_method is shipment_capped.

        This ensures that the shipment cost is added when the shipment is
        created and not when the invoice is processed.
        """
        result = super(Sale, self)._get_invoice_line_sale_line(invoice_type)
        if self.shipment_cost_method == 'shipment_capped':
            for line in self.lines:
                if line.id in result and line.shipment_cost:
                    del result[line.id]
        return result

    def create_invoice(self, invoice_type):
        """
        Change invoice creation behavior to also create a shipment based
        invoice line if required.
        """
        pool = Pool()
        Invoice = pool.get('account.invoice')
        Shipment = pool.get('stock.shipment.out')

        invoice = super(Sale, self).create_invoice(invoice_type)

        if (invoice
                and invoice_type == 'out_invoice'
                and self.shipment_cost_method == 'shipment_capped'):
            with Transaction().set_user(0, set_context=True):
                invoice = Invoice(invoice.id)
            for shipment in self.shipments:
                if (shipment.state == 'done'
                        and shipment.carrier
                        and shipment.cost
                        and not shipment.cost_invoice_line):
                    invoice_line = shipment.get_cost_invoice_line(invoice)
                    if not invoice_line:
                        continue  # pragma: no cover

                    # now check if the invoice line's amount crosses the
                    # shipment charges remaining to be invoices
                    shipment_amount_remaining = self.currency.round(max(
                        Decimal('0'),
                        self.shipment_amount - self.shipment_amount_invoiced
                    ))
                    if not shipment_amount_remaining:
                        continue

                    # Change unit price to the lower of the cost of
                    # shipment or the amount remaining.
                    invoice_line.unit_price = min(
                        shipment_amount_remaining,
                        invoice_line.unit_price
                    )

                    invoice_line.invoice = invoice
                    invoice_line.save()

                    Shipment.write([shipment], {
                        'cost_invoice_line': invoice_line.id,
                    })

            with Transaction().set_user(0, set_context=True):
                Invoice.update_taxes([invoice])

        return invoice
