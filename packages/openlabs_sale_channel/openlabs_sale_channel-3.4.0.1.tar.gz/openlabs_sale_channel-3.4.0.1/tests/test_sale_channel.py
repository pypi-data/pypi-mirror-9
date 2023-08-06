# -*- coding: utf-8 -*-
"""
    tests/test_sale_channel.py

    :copyright: (C) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
import unittest
from contextlib import nested

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.exceptions import UserError
from trytond.transaction import Transaction
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))


class BaseTestCase(unittest.TestCase):
    '''
    Base Test Case sale payment module.
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('sale_channel')

        self.Currency = POOL.get('currency.currency')
        self.Company = POOL.get('company.company')
        self.Party = POOL.get('party.party')
        self.User = POOL.get('res.user')
        self.Country = POOL.get('country.country')
        self.Subdivision = POOL.get('country.subdivision')
        self.Sale = POOL.get('sale.sale')
        self.SaleLine = POOL.get('sale.line')
        self.SaleChannel = POOL.get('sale.channel')
        self.Location = POOL.get('stock.location')
        self.PriceList = POOL.get('product.price_list')
        self.Payment_Term = POOL.get('account.invoice.payment_term')
        self.Sequence = POOL.get('ir.sequence')
        self.Group = POOL.get('res.group')

    def _create_payment_term(self):
        """Create a simple payment term with all advance
        """
        PaymentTerm = POOL.get('account.invoice.payment_term')

        return PaymentTerm.create([{
            'name': 'Direct',
            'lines': [('create', [{'type': 'remainder'}])]
        }])

    def setup_defaults(self):
        """Creates default data for testing
        """
        self.currency, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])

        # Create a payment term
        self.payment_term, = self._create_payment_term()

        self.country, = self.Country.create([{
            'name': 'United States of America',
            'code': 'US',
        }])

        self.subdivision, = self.Subdivision.create([{
            'country': self.country.id,
            'name': 'California',
            'code': 'CA',
            'type': 'state',
        }])

        # Create party
        with Transaction().set_context(company=None):
            self.company_party, self.sale_party = self.Party.create([{
                'name': 'Openlabs',
                'addresses': [('create', [{
                    'name': 'Openlabs',
                    'city': 'Gothom',
                    'country': self.country.id,
                    'subdivision': self.subdivision.id,
                }])],
                'customer_payment_term': self.payment_term.id,
            }, {
                'name': 'John Wick',
                'addresses': [('create', [{
                    'name': 'John Wick',
                    'city': 'Gothom',
                    'country': self.country.id,
                    'subdivision': self.subdivision.id,
                }, {
                    'name': 'John Doe',
                    'city': 'Gothom',
                    'country': self.country.id,
                    'subdivision': self.subdivision.id,
                }])],
                'customer_payment_term': self.payment_term.id,
            }])

        self.company, = self.Company.create([{
            'party': self.company_party,
            'currency': self.currency
        }])

        user = self.User(USER)
        self.User.write([user], {
            'company': self.company,
            'main_company': self.company,
        })

        self.sales_user, = self.User.create([{
            'name': 'Sales Person',
            'login': 'sale',
            'company': self.company,
            'main_company': self.company,
            'groups': [('add', [
                self.Group.search([('name', '=', 'Sales')])[0].id
            ])]
        }])

        self.price_list = self.PriceList(
            name='PL 1',
            company=self.company
        )
        self.price_list.save()

        with Transaction().set_context(company=self.company.id):
            self.channel1, self.channel2, self.channel3, self.channel4 = \
                self.SaleChannel.create([{
                    'name': 'Channel 1',
                    'code': 'C1',
                    'address': self.company_party.addresses[0].id,
                    'source': 'manual',
                    'warehouse': self.Location.search([
                        ('code', '=', 'WH')
                    ])[0].id,
                    'invoice_method': 'manual',
                    'shipment_method': 'manual',
                    'payment_term': self.payment_term.id,
                    'price_list': self.price_list,
                }, {
                    'name': 'Channel 2',
                    'code': 'C2',
                    'address': self.company_party.addresses[0].id,
                    'source': 'manual',
                    'warehouse': self.Location.search([
                        ('code', '=', 'WH')
                    ])[0].id,
                    'invoice_method': 'manual',
                    'shipment_method': 'manual',
                    'payment_term': self.payment_term.id,
                    'price_list': self.price_list,
                    'read_users': [('add', [self.sales_user.id])],
                }, {
                    'name': 'Channel 3',
                    'code': 'C3',
                    'address': self.company_party.addresses[0].id,
                    'source': 'manual',
                    'warehouse': self.Location.search([
                        ('code', '=', 'WH')
                    ])[0].id,
                    'invoice_method': 'manual',
                    'shipment_method': 'manual',
                    'payment_term': self.payment_term.id,
                    'price_list': self.price_list,
                    'read_users': [('add', [self.sales_user.id])],
                    'create_users': [('add', [self.sales_user.id])],
                }, {
                    'name': 'Channel 4',
                    'code': 'C4',
                    'address': self.company_party.addresses[0].id,
                    'source': 'manual',
                    'warehouse': self.Location.search([
                        ('code', '=', 'WH')
                    ])[0].id,
                    'invoice_method': 'manual',
                    'shipment_method': 'manual',
                    'payment_term': self.payment_term.id,
                    'price_list': self.price_list,
                    'read_users': [('add', [self.sales_user.id])],
                    'create_users': [('add', [self.sales_user.id])],
                }])

        self.sales_user.current_channel = self.channel3
        self.sales_user.save()
        self.assertTrue(self.channel3.rec_name in self.sales_user.status_bar)

        # Save IDs to share between transactions
        self.sales_user_id = self.sales_user.id

    def create_sale(self, res_user_id, channel=None):
        """
        Create sale in new transaction
        """
        with nested(
                Transaction().set_user(res_user_id),
                Transaction().set_context(
                    company=self.company.id, current_channel=channel
                )):
            sale = self.Sale(
                party=self.sale_party,
                invoice_address=self.sale_party.addresses[0],
                shipment_address=self.sale_party.addresses[0],
                lines=[],
            )
            sale.save()
            sale.on_change_channel()
            sale.on_change_with_channel()
            self.assertEqual(sale.invoice_method, 'manual')
            return sale


class TestSaleChannel(BaseTestCase):
    """
    Test Sale Channel Module
    """
    def test_0010_permission_sale_admin(self):
        SALE_ADMIN = USER
        with Transaction().start(DB_NAME, SALE_ADMIN, context=CONTEXT):
            self.setup_defaults()

            #      USER       Channel1    Channel2    Channel3  Channel4
            #    sale_user       -           R           RW       RW
            #    sale_admin     N/A         N/A         N/A      N/A

            # Creating sale with admin(sale_admin) user
            self.create_sale(SALE_ADMIN, self.channel1)
            self.create_sale(SALE_ADMIN, self.channel2)
            self.create_sale(SALE_ADMIN, self.channel3)
            self.create_sale(SALE_ADMIN, self.channel4)

    def test_0020_permission_sale_user(self):
        """
        Cannot create on channel without any permissions
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as txn:
            self.setup_defaults()

            #      USER       Channel1    Channel2    Channel3  Channel4
            #    sale_user       -           R           RW       RW
            #    sale_admin     N/A         N/A         N/A      N/A

            with self.assertRaises(UserError):
                # Can not create without create_permission
                self.create_sale(self.sales_user_id, self.channel1)

            txn.cursor.rollback()

    def test_0030_permission_sale_user(self):
        """
        Cannot create sale on readonly channel
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as txn:
            self.setup_defaults()

            #      USER       Channel1    Channel2    Channel3  Channel4
            #    sale_user       -           R           RW       RW
            #    sale_admin     N/A         N/A         N/A      N/A

            with self.assertRaises(UserError):
                # Can not create using Read channel
                self.create_sale(self.sales_user_id, self.channel2)

            txn.cursor.rollback()

    def test_0040_permission_sale_user(self):
        """
        Ability to read orders in channels the user has access to
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as txn:
            self.setup_defaults()

            # Create a bunch of orders first
            SALE_ADMIN = USER
            sale1 = self.create_sale(SALE_ADMIN, self.channel1)
            sale2 = self.create_sale(SALE_ADMIN, self.channel2)
            sale3 = self.create_sale(SALE_ADMIN, self.channel3)
            sale4 = self.create_sale(SALE_ADMIN, self.channel4)

            #      USER       Channel1    Channel2    Channel3  Channel4
            #    sale_user       -           R           RW       RW
            #    sale_admin     N/A         N/A         N/A      N/A

            with Transaction().set_user(self.sales_user_id):
                sales = self.Sale.search([])

                self.assertEqual(len(sales), 3)
                self.assertTrue(sale1 not in sales)  # No Access
                self.assertTrue(sale2 in sales)      # R
                self.assertTrue(sale3 in sales)      # RW
                self.assertTrue(sale4 in sales)      # RW

            txn.cursor.rollback()

    def test_0050_permission_sale_user(self):
        """
        Cannot edit sale on channel with no access
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as txn:
            self.setup_defaults()

            #      USER       Channel1    Channel2    Channel3  Channel4
            #    sale_user       -           R           RW       RW
            #    sale_admin     N/A         N/A         N/A      N/A

            sale1 = self.create_sale(USER, self.channel1)

            with self.assertRaises(UserError):
                with Transaction().set_user(self.sales_user_id):
                    sale1 = self.Sale(sale1.id)
                    # Try write on No Access Channel's Sale
                    sale1.invoice_address = self.sale_party.addresses[1]
                    sale1.save()

            txn.cursor.rollback()

    def test_0060_permission_sale_user(self):
        """
        CAN edit sale on Create/Read channel
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as txn:
            self.setup_defaults()

            #      USER       Channel1    Channel2    Channel3  Channel4
            #    sale_user       -           R           RW       RW
            #    sale_admin     N/A         N/A         N/A      N/A

            sale2 = self.create_sale(USER, self.channel2)
            sale3 = self.create_sale(USER, self.channel3)

            with Transaction().set_user(self.sales_user_id):
                sale2 = self.Sale(sale2.id)
                sale3 = self.Sale(sale3.id)

                sale3.invoice_address = self.sale_party.addresses[1]
                sale3.save()

                self.assertEqual(
                    sale3.invoice_address, self.sale_party.addresses[1]
                )

                sale2.invoice_address = self.sale_party.addresses[1]
                sale2.save()

            txn.cursor.rollback()

    def test_0070_state_change(self):
        """
        No matter who you are, cannot change channel on quote state
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT) as txn:
            self.setup_defaults()

            #      USER       Channel1    Channel2    Channel3  Channel4
            #    sale_user       -           R           RW       RW
            #    sale_admin     N/A         N/A         N/A      N/A
            sale3 = self.create_sale(USER, self.channel3)
            self.Sale.quote([sale3])
            self.assertEqual(sale3.state, 'quotation')

            with self.assertRaises(UserError):
                sale3.channel = self.channel4
                sale3.save()

            txn.cursor.rollback()


def suite():
    """
    Define Suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestSaleChannel)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
