# -*- coding: utf-8 -*-
"""
    tests/test_views_depends.py

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
from datetime import date
from decimal import Decimal

from trytond.tests.test_tryton import DB_NAME, USER, CONTEXT, POOL
import trytond.tests.test_tryton
from trytond.transaction import Transaction


class TestShipmentCostCap(unittest.TestCase):
    """
    Test Shipment Cost Cap
    """

    def setUp(self):
        """
        Set up data used in the tests.
        """
        trytond.tests.test_tryton.install_module('sale_shipment_cost_cap')

        self.Currency = POOL.get('currency.currency')
        self.Company = POOL.get('company.company')
        self.Party = POOL.get('party.party')
        self.User = POOL.get('res.user')
        self.Country = POOL.get('country.country')
        self.SubDivision = POOL.get('country.subdivision')
        self.Carrier = POOL.get('carrier')

    def _create_coa_minimal(self, company):
        """Create a minimal chart of accounts
        """
        AccountTemplate = POOL.get('account.account.template')
        Account = POOL.get('account.account')

        account_create_chart = POOL.get(
            'account.create_chart', type="wizard"
        )

        account_template, = AccountTemplate.search(
            [('parent', '=', None)]
        )

        session_id, _, _ = account_create_chart.create()
        create_chart = account_create_chart(session_id)
        create_chart.account.account_template = account_template
        create_chart.account.company = company
        create_chart.transition_create_account()

        receivable, = Account.search([
            ('kind', '=', 'receivable'),
            ('company', '=', company),
        ])
        payable, = Account.search([
            ('kind', '=', 'payable'),
            ('company', '=', company),
        ])
        create_chart.properties.company = company
        create_chart.properties.account_receivable = receivable
        create_chart.properties.account_payable = payable
        create_chart.transition_create_properties()

    def _get_account_by_kind(self, kind, company=None, silent=True):
        """Returns an account with given spec

        :param kind: receivable/payable/expense/revenue
        :param silent: dont raise error if account is not found
        """
        Account = POOL.get('account.account')
        Company = POOL.get('company.company')

        if company is None:
            company, = Company.search([], limit=1)

        accounts = Account.search([
            ('kind', '=', kind),
            ('company', '=', company)
        ], limit=1)
        if not accounts and not silent:
            raise Exception("Account not found")
        return accounts[0] if accounts else False

    def _create_payment_term(self):
        """Create a simple payment term with all advance
        """
        PaymentTerm = POOL.get('account.invoice.payment_term')

        return PaymentTerm.create([{
            'name': 'Direct',
            'lines': [('create', [{'type': 'remainder'}])]
        }])[0]

    def setup_defaults(self):
        """
        Setup the defaults
        """
        User = POOL.get('res.user')
        Uom = POOL.get('product.uom')
        Template = POOL.get('product.template')
        Product = POOL.get('product.product')
        SaleConfig = POOL.get('sale.configuration')

        self.usd, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])

        with Transaction().set_context(company=None):
            self.party, = self.Party.create([{
                'name': 'Openlabs',
            }])
            self.company, = self.Company.create([{
                'party': self.party.id,
                'currency': self.usd
            }])

        User.write(
            [User(USER)], {
                'main_company': self.company.id,
                'company': self.company.id,
            }
        )

        self._create_coa_minimal(company=self.company.id)
        self.account_revenue = self._get_account_by_kind('revenue')
        self.account_expense = self._get_account_by_kind('expense')
        self._create_payment_term()

        carrier_party, = self.Party.create([{
            'name': 'Carrier Party',
        }])

        self.party1, = self.Party.create([{
            'name': 'Test party',
            'addresses': [('create', [{
                'city': 'Melbourne',
            }])],
        }])

        self.uom, = Uom.search([('name', '=', 'Unit')])

        self.template1, = Template.create([{
            'name': 'product',
            'type': 'goods',
            'list_price': Decimal('10'),
            'cost_price': Decimal('5'),
            'default_uom': self.uom.id,
            'salable': True,
            'sale_uom': self.uom.id,
            'account_revenue': self.account_revenue.id,
        }])

        self.template2, = Template.create([{
            'name': 'product2',
            'type': 'goods',
            'list_price': Decimal('20'),
            'cost_price': Decimal('5'),
            'default_uom': self.uom.id,
            'salable': True,
            'sale_uom': self.uom.id,
            'account_revenue': self.account_revenue.id,
        }])

        self.product1, = Product.create([{
            'template': self.template1.id,
        }])

        self.product2, = Product.create([{
            'template': self.template2.id,
        }])

        self.shipping_template, = Template.create([{
            'name': 'shipment',
            'type': 'service',
            'list_price': Decimal('20'),
            'cost_price': Decimal('5'),
            'default_uom': self.uom.id,
            'salable': True,
            'sale_uom': self.uom.id,
            'account_revenue': self.account_revenue.id,
        }])

        self.shipping_product, = Product.create([{
            'template': self.shipping_template.id,
        }])

        self.carrier_product_temp, = Template.create([{
            'name': 'carrier_produict',
            'type': 'service',
            'list_price': Decimal('1'),
            'cost_price': Decimal('1'),
            'default_uom': self.uom.id,
            'salable': True,
            'sale_uom': self.uom.id,
            'account_revenue': self.account_revenue.id,
        }])

        carrier_product, = Product.create([{
            'template': self.carrier_product_temp.id,
        }])

        self.carrier, = self.Carrier.create([{
            'party': carrier_party,
            'carrier_product': carrier_product,
        }])

        SaleConfig.write([SaleConfig(1)], {
            'sale_carrier': self.carrier.id,
            'sale_invoice_method': 'shipment',
            'sale_shipment_method': 'order',
            'sale_shipment_cost_method': 'shipment_capped',
        })

    def test0010_single_shipment_cost(self):
        """
        Check if single invoice on single shipment
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            Sale = POOL.get('sale.sale')
            ShipmentOut = POOL.get('stock.shipment.out')

            self.setup_defaults()
            with Transaction().set_context({'company': self.company.id}):
                shipment_cost = Decimal('30')
                sale, = Sale.create([{
                    'reference': 'Sale1',
                    'sale_date': date.today(),
                    'invoice_address': self.party1.addresses[0].id,
                    'shipment_address': self.party1.addresses[0].id,
                    'party': self.party1.id,
                    'carrier': self.carrier.id,
                    'invoice_method': 'shipment',
                    'shipment_method': 'order',
                    'shipment_cost_method': 'shipment_capped',
                    'lines': [
                        ('create', [{
                            'type': 'line',
                            'quantity': 5,
                            'unit': self.uom,
                            'unit_price': 10,
                            'description': 'Test description1',
                            'product': self.product1.id,
                        }, {
                            'type': 'line',
                            'quantity': 2,
                            'unit': self.uom,
                            'unit_price': 20,
                            'description': 'Test description1',
                            'product': self.product1.id,
                        }, {
                            'type': 'line',
                            'quantity': 1,
                            'unit': self.uom,
                            'unit_price': shipment_cost,
                            'description': 'Shipping',
                            'product': self.shipping_product.id,
                            'shipment_cost': shipment_cost
                        }])
                    ]
                }])

                Sale.quote([sale])
                Sale.confirm([sale])
                Sale.process([sale])

                self.assertEqual(sale.state, 'processing')
                self.assertEqual(len(sale.invoices), 0)

                shipment, = sale.shipments
                shipment.cost = Decimal(25)
                shipment.save()
                ShipmentOut.assign([shipment])
                ShipmentOut.pack([shipment])
                ShipmentOut.done([shipment])
                self.assertEqual(shipment.state, 'done')

                self.assertEqual(len(sale.invoices), 1)
                self.assertEqual(sale.invoices[0].total_amount, Decimal('115'))

    def test0020_multiple_shipment_cost(self):
        """
        Check if multiple invoice on multiple shipment

            Case 2:

              Sale 1 with 2 shipments and each costs 15
              Test: Invoice total is (50 + 15) and (40 + 15) = 120
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            Sale = POOL.get('sale.sale')
            ShipmentOut = POOL.get('stock.shipment.out')

            self.setup_defaults()
            with Transaction().set_context({'company': self.company.id}):
                total_shipment_cost = Decimal('30')
                sale, = Sale.create([{
                    'reference': 'Sale1',
                    'sale_date': date.today(),
                    'invoice_address': self.party1.addresses[0].id,
                    'shipment_address': self.party1.addresses[0].id,
                    'party': self.party1.id,
                    'carrier': self.carrier.id,
                    'invoice_method': 'shipment',
                    'shipment_method': 'order',
                    'shipment_cost_method': 'shipment_capped',
                    'lines': [
                        ('create', [{
                            'type': 'line',
                            'quantity': 5,
                            'unit': self.uom,
                            'unit_price': 10,
                            'description': 'Test description1',
                            'product': self.product1.id,
                        }, {
                            'type': 'line',
                            'quantity': 2,
                            'unit': self.uom,
                            'unit_price': 20,
                            'description': 'Test description1',
                            'product': self.product2.id,
                        }, {
                            'type': 'line',
                            'quantity': 1,
                            'unit': self.uom,
                            'unit_price': total_shipment_cost,
                            'description': 'Shipping',
                            'product': self.shipping_product.id,
                            'shipment_cost': total_shipment_cost
                        }])
                    ]
                }])

                Sale.quote([sale])
                Sale.confirm([sale])
                Sale.process([sale])

                self.assertEqual(sale.state, 'processing')
                self.assertEqual(len(sale.invoices), 0)

                shipment1, = sale.shipments
                shipment1.cost = Decimal(15)
                shipment1.save()
                self.assertEqual(len(shipment1.outgoing_moves), 2)

                # Delete a shipment Move
                ShipmentOut.write([shipment1], {
                    'moves': [('remove', [shipment1.inventory_moves[0].id])]
                })
                ShipmentOut.assign([shipment1])
                ShipmentOut.pack([shipment1])
                ShipmentOut.done([shipment1])

                # Select other shipment
                shipment2, = filter(
                    lambda s: s.id != shipment1.id, sale.shipments
                )
                shipment2.cost = Decimal(15)
                shipment2.save()

                ShipmentOut.assign([shipment2])
                ShipmentOut.pack([shipment2])
                ShipmentOut.done([shipment2])
                for shipment in sale.shipments:
                    self.assertEqual(shipment.state, 'done')

                self.assertEqual(len(sale.invoices), 2)
                total_amount = sum([
                    inv.total_amount for inv in sale.invoices
                ])
                self.assertEqual(total_amount, Decimal('120'))

    def test0030_multiple_shipment_cost(self):
        """
        Check if single invoice on single shipment

            Case 3:
              Sale 1 with 3 shipment and each costs 15
            Test:
              Invoice total is (50 + 15) + (40 + 15) + (60 + 0) = 180
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            Sale = POOL.get('sale.sale')
            ShipmentOut = POOL.get('stock.shipment.out')

            self.setup_defaults()
            with Transaction().set_context({'company': self.company.id}):
                total_shipment_cost = Decimal('30')
                sale, = Sale.create([{
                    'reference': 'Sale1',
                    'sale_date': date.today(),
                    'invoice_address': self.party1.addresses[0].id,
                    'shipment_address': self.party1.addresses[0].id,
                    'party': self.party1.id,
                    'carrier': self.carrier.id,
                    'invoice_method': 'shipment',
                    'shipment_method': 'order',
                    'shipment_cost_method': 'shipment_capped',
                    'lines': [
                        ('create', [{
                            'type': 'line',
                            'quantity': 5,
                            'unit': self.uom,
                            'unit_price': 10,
                            'description': 'Test description1',
                            'product': self.product1.id,
                        }, {
                            'type': 'line',
                            'quantity': 2,
                            'unit': self.uom,
                            'unit_price': 20,
                            'description': 'Test description1',
                            'product': self.product2.id,
                        }, {
                            'type': 'line',
                            'quantity': 3,
                            'unit': self.uom,
                            'unit_price': 20,
                            'description': 'Test description2',
                            'product': self.product2.id,
                        }, {
                            'type': 'line',
                            'quantity': 1,
                            'unit': self.uom,
                            'unit_price': total_shipment_cost,
                            'description': 'Shipping',
                            'product': self.shipping_product.id,
                            'shipment_cost': total_shipment_cost
                        }])
                    ]
                }])

                Sale.quote([sale])
                Sale.confirm([sale])
                Sale.process([sale])

                self.assertEqual(sale.state, 'processing')
                self.assertEqual(len(sale.invoices), 0)

                shipment1, = sale.shipments
                shipment1.cost = Decimal(15)
                shipment1.save()
                self.assertEqual(len(shipment1.outgoing_moves), 3)

                # Delete a shipment Move
                ShipmentOut.write([shipment1], {
                    'moves': [('remove', [
                        shipment1.inventory_moves[0].id,
                        shipment1.inventory_moves[1].id
                    ])]
                })
                ShipmentOut.assign([shipment1])
                ShipmentOut.pack([shipment1])
                ShipmentOut.done([shipment1])

                # Select other shipment
                shipment2, = filter(
                    lambda s: s.id != shipment1.id, sale.shipments
                )
                shipment2.cost = Decimal(15)
                shipment2.save()
                self.assertEqual(len(shipment2.outgoing_moves), 2)

                # Delete a shipment Move
                ShipmentOut.write([shipment2], {
                    'moves': [('remove', [
                        shipment2.inventory_moves[0].id,
                    ])]
                })
                ShipmentOut.assign([shipment2])
                ShipmentOut.pack([shipment2])
                ShipmentOut.done([shipment2])

                # Select other shipment
                shipment3, = filter(
                    lambda s: s.id not in [shipment2.id, shipment1.id],
                    sale.shipments
                )
                shipment3.cost = Decimal(15)
                shipment3.save()
                self.assertEqual(len(shipment3.outgoing_moves), 1)

                ShipmentOut.assign([shipment3])
                ShipmentOut.pack([shipment3])
                ShipmentOut.done([shipment3])

                for shipment in sale.shipments:
                    self.assertEqual(shipment.state, 'done')

                self.assertEqual(len(sale.invoices), 3)
                total_amount = sum([
                    inv.total_amount for inv in sale.invoices
                ])
                self.assertEqual(total_amount, Decimal('180'))

    def test0040_shipment_cost_on_order(self):
        """
        Check shipment cost method is order
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            Sale = POOL.get('sale.sale')
            ShipmentOut = POOL.get('stock.shipment.out')

            self.setup_defaults()
            with Transaction().set_context({'company': self.company.id}):
                shipment_cost = Decimal('30')
                sale, = Sale.create([{
                    'reference': 'Sale1',
                    'sale_date': date.today(),
                    'invoice_address': self.party1.addresses[0].id,
                    'shipment_address': self.party1.addresses[0].id,
                    'party': self.party1.id,
                    'carrier': self.carrier.id,
                    'invoice_method': 'shipment',
                    'shipment_method': 'order',
                    'shipment_cost_method': 'order',
                    'lines': [
                        ('create', [{
                            'type': 'line',
                            'quantity': 5,
                            'unit': self.uom,
                            'unit_price': 10,
                            'description': 'Test description1',
                            'product': self.product1.id,
                        }, {
                            'type': 'line',
                            'quantity': 2,
                            'unit': self.uom,
                            'unit_price': 20,
                            'description': 'Test description1',
                            'product': self.product2.id,
                        }, {
                            'type': 'line',
                            'quantity': 1,
                            'unit': self.uom,
                            'unit_price': shipment_cost,
                            'description': 'Shipping',
                            'product': self.shipping_product.id,
                            'shipment_cost': shipment_cost
                        }])
                    ]
                }])

                Sale.quote([sale])
                Sale.confirm([sale])
                Sale.process([sale])

                self.assertEqual(sale.state, 'processing')
                self.assertEqual(len(sale.invoices), 1)
                # Just the shipment cost
                invoice = sale.invoices[0]
                self.assertEqual(invoice.total_amount, Decimal('30'))

                shipment, = sale.shipments
                shipment.cost = Decimal(30)
                shipment.save()
                self.assertEqual(len(shipment.outgoing_moves), 2)

                ShipmentOut.assign([shipment])
                ShipmentOut.pack([shipment])
                ShipmentOut.done([shipment])

                self.assertEqual(len(sale.invoices), 2)
                for inv in sale.invoices:
                    if inv.id == invoice.id:
                        # Ignore previous invoice
                        continue
                    # Sale Amount
                    self.assertEqual(inv.total_amount, Decimal('90'))
                    break
                else:
                    self.fail('No invoice for shipment')

    def test0050_shipment_cost_on_shipment(self):
        """
        Check shipment cost method is shipment
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            Sale = POOL.get('sale.sale')
            ShipmentOut = POOL.get('stock.shipment.out')

            self.setup_defaults()
            with Transaction().set_context({'company': self.company.id}):
                shipment_cost = Decimal('30')
                sale, = Sale.create([{
                    'reference': 'Sale1',
                    'sale_date': date.today(),
                    'invoice_address': self.party1.addresses[0].id,
                    'shipment_address': self.party1.addresses[0].id,
                    'party': self.party1.id,
                    'carrier': self.carrier.id,
                    'invoice_method': 'shipment',
                    'shipment_method': 'order',
                    'shipment_cost_method': 'shipment',
                    'lines': [
                        ('create', [{
                            'type': 'line',
                            'quantity': 5,
                            'unit': self.uom,
                            'unit_price': 10,
                            'description': 'Test description1',
                            'product': self.product1.id,
                        }, {
                            'type': 'line',
                            'quantity': 2,
                            'unit': self.uom,
                            'unit_price': 20,
                            'description': 'Test description1',
                            'product': self.product2.id,
                        }, {
                            'type': 'line',
                            'quantity': 1,
                            'unit': self.uom,
                            'unit_price': shipment_cost,
                            'description': 'Shipping',
                            'product': self.shipping_product.id,
                            'shipment_cost': shipment_cost
                        }])
                    ]
                }])

                Sale.quote([sale])
                Sale.confirm([sale])
                Sale.process([sale])

                self.assertEqual(sale.state, 'processing')
                self.assertEqual(len(sale.invoices), 0)

                shipment, = sale.shipments
                shipment.cost = Decimal(30)
                shipment.save()
                self.assertEqual(len(shipment.outgoing_moves), 2)

                ShipmentOut.assign([shipment])
                ShipmentOut.pack([shipment])
                ShipmentOut.done([shipment])

                self.assertEqual(len(sale.invoices), 1)
                # Just the shipment cost
                self.assertEqual(sale.invoices[0].total_amount, Decimal('120'))


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestShipmentCostCap)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
