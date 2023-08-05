# -*- coding: utf-8 -*-
"""
    tests/test_inventory.py
    :copyright: (C) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
import datetime
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from trytond.transaction import Transaction
from trytond.pyson import Eval
from trytond.pool import Pool


class TestInventory(unittest.TestCase):
    """
    Tests for Inventory Report
    """

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('inventory_report')

        self.Currency = POOL.get('currency.currency')
        self.Company = POOL.get('company.company')
        self.Party = POOL.get('party.party')
        self.User = POOL.get('res.user')
        self.ProductTemplate = POOL.get('product.template')
        self.Uom = POOL.get('product.uom')
        self.ProductCategory = POOL.get('product.category')
        self.Product = POOL.get('product.product')
        self.Country = POOL.get('country.country')
        self.Subdivision = POOL.get('country.subdivision')
        self.Employee = POOL.get('company.employee')
        self.Group = POOL.get('res.group')
        self.Country = POOL.get('country.country')
        self.Subdivision = POOL.get('country.subdivision')
        self.Inventory = POOL.get('stock.inventory')
        self.Location = POOL.get('stock.location')

    def setup_defaults(self):
        """Creates default data for testing
        """
        currency, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])

        with Transaction().set_context(company=None):
            company_party, = self.Party.create([{
                'name': 'Openlabs'
            }])

        self.company, = self.Company.create([{
            'party': company_party,
            'currency': currency,
        }])

        self.User.write([self.User(USER)], {
            'company': self.company,
            'main_company': self.company,
        })

        CONTEXT.update(self.User.get_preferences(context_only=True))

        self.uom, = self.Uom.search([('symbol', '=', 'u')])

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

        # Add address to company's party record
        self.Party.write([self.company.party], {
            'addresses': [('create', [{
                'name': 'Openlabs',
                'party': Eval('id'),
                'city': 'Los Angeles',
                'country': self.country.id,
                'subdivision': self.subdivision.id,
            }])],
        })

        self.product_category, = self.ProductCategory.create([{
            'name': 'Automobile',
        }])

        self.product_template, = self.ProductTemplate.create([{
            'name': 'Bat Mobile',
            'type': 'goods',
            'list_price': Decimal('2000'),
            'cost_price': Decimal('1500'),
            'category': self.product_category.id,
            'default_uom': self.uom,
        }])

        self.product, = self.Product.create([{
            'template': self.product_template.id,
            'code': '123',
        }])

        self.location, = self.Location.create([{
            'name': 'Storage Out'
        }])

    def test_0010_test_inventory_report(self):
        """
        Test inventory report execution
        """
        ActionReport = POOL.get('ir.action.report')
        Report = POOL.get('report.stock_inventory', type="report")

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            report_action, = ActionReport.search([
                ('report_name', '=', 'report.stock_inventory'),
                ('name', '=', 'Inventory')
            ])
            report_action.extension = 'pdf'
            report_action.save()

            with Transaction().set_context(company=self.company.id):
                inventory, = self.Inventory.create([{
                    'location': self.location,
                    'date': datetime.date.today(),
                    'lines': [('create', [{
                        'product': self.product,
                        'quantity': 20,
                    }])]
                }])

                # Set Pool.test as False as we need the report to be generated
                # as PDF
                # This is specifically to cover the PDF coversion code
                Pool.test = False

                # Generate Inventory report
                val = Report.execute([inventory.id], {})

                # Revert Pool.test back to True for other tests to run normally
                Pool.test = True

                self.assert_(val)
                # Assert report type
                self.assertEqual(val[0], 'pdf')
                # Assert report name
                self.assertEqual(val[3], 'Inventory')


def suite():
    "Define suite"
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestInventory)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
