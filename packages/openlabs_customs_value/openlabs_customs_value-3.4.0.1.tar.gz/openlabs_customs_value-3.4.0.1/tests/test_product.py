# -*- coding: utf-8 -*-
"""
    test_product.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction
from decimal import Decimal

DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))


class TestBase(unittest.TestCase):
    """
    Base Test Case
    """

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('customs_value')

        self.Product = POOL.get('product.product')
        self.Template = POOL.get('product.template')
        self.Uom = POOL.get('product.uom')

    def create_product_template(self):
        """
        Creates default product template
        """
        self.uom, = self.Uom.search([('name', '=', 'Unit')])

        return self.Template.create([{
            'name': 'product',
            'list_price': Decimal('20'),
            'cost_price': Decimal('5'),
            'default_uom': self.uom.id,
        }])[0]


class TestProduct(TestBase):
    '''
    Test Product
    '''

    def test0010_check_product_custom_value(self):
        """
        Check custom value for product
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):

            template = self.create_product_template()

            product, = self.Product.create([{
                'template': template,
            }])

            self.assertEqual(
                product.use_list_price_as_customs_value, True
            )

            self.assertEqual(product.customs_value_used, product.list_price)

            product, = self.Product.create([{
                'template': template,
                'customs_value': Decimal('50'),
                'use_list_price_as_customs_value': False
            }])

            self.assertEqual(
                product.use_list_price_as_customs_value, False
            )

            self.assertEqual(product.customs_value_used, product.customs_value)

            product, = self.Product.create([{
                'template': template,
                'customs_value': Decimal('50'),
                'use_list_price_as_customs_value': True
            }])

            self.assertEqual(
                product.use_list_price_as_customs_value, True
            )

            self.assertEqual(product.customs_value_used, product.list_price)


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestProduct)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
