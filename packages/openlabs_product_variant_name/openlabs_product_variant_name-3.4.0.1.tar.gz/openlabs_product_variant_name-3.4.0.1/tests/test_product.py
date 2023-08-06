# -*- coding: utf-8 -*-
"""
    tests/test_product.py
    :copyright: (C) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from trytond.transaction import Transaction


class TestProduct(unittest.TestCase):
    """
    Test Product
    """

    def setUp(self):
        """
        setUp method.
        """
        trytond.tests.test_tryton.install_module('product_variant_name')

        self.Product = POOL.get('product.product')
        self.Template = POOL.get('product.template')
        self.Uom = POOL.get('product.uom')

    def test0010_product_name(self):
        """
        Tests the searcher on the name field.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            uom, = self.Uom.search([], limit=1)
            template1, = self.Template.create([{
                'name': 'ThisIsProduct',
                'type': 'goods',
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'default_uom': uom.id,
            }])

            product1, = self.Product.create([{
                'template': template1.id,
                'code': 'SomeProductCode',
            }])
            product2, = self.Product.create([{
                'template': template1.id,
                'code': 'SomeProductCode2',
                'variant_name': 'ADifferentName',
            }])

            products = self.Product.search([
                ('name', '=', 'ThisIsProduct'),
            ])
            self.assertEqual(len(products), 2)

            products = self.Product.search([
                ('name', '=', 'ADifferentName'),
            ])
            self.assertEqual(len(products), 1)
            self.assertEqual(products[0].id, product2.id)

            product1.variant_name = 'ChangedName'
            product1.save()

            products = self.Product.search([
                ('name', '=', 'ThisIsProduct'),
            ])
            self.assertEqual(len(products), 2)
