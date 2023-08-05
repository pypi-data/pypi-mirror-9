# -*- coding: utf-8 -*-
"""
    tests/test_product.py

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))
import unittest
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from nereid.testing import NereidTestCase
from trytond.transaction import Transaction
from trytond.exceptions import UserError


class TestProduct(NereidTestCase):
    "Product Test Case"

    def setup_defaults(self):
        """
        Setup the defaults
        """
        usd, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])
        party1, = self.Party.create([{
            'name': 'Openlabs',
        }])
        company, = self.Company.create([{
            'party': party1.id,
            'currency': usd.id
        }])
        party2, = self.Party.create([{
            'name': 'Guest User',
        }])
        party3, = self.Party.create([{
            'name': 'Registered User',
        }])
        self.registered_user, = self.NereidUser.create([{
            'party': party3.id,
            'display_name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': company.id,
        }])

        # Create website
        url_map, = self.UrlMap.search([], limit=1)
        en_us, = self.Language.search([('code', '=', 'en_US')])

        self.locale_en_us, = self.Locale.create([{
            'code': 'en_US',
            'language': en_us.id,
            'currency': usd.id,
        }])
        self.NereidWebsite.create([{
            'name': 'localhost',
            'url_map': url_map.id,
            'company': company.id,
            'application_user': USER,
            'default_locale': self.locale_en_us.id,
            'currencies': [('add', [usd.id])],
        }])

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test execution.
        """
        trytond.tests.test_tryton.install_module('nereid_catalog_variants')

        self.Currency = POOL.get('currency.currency')
        self.Site = POOL.get('nereid.website')
        self.Product = POOL.get('product.product')
        self.Company = POOL.get('company.company')
        self.NereidUser = POOL.get('nereid.user')
        self.UrlMap = POOL.get('nereid.url_map')
        self.Language = POOL.get('ir.lang')
        self.NereidWebsite = POOL.get('nereid.website')
        self.Party = POOL.get('party.party')
        self.Template = POOL.get('product.template')
        self.Uom = POOL.get('product.uom')
        self.Locale = POOL.get('nereid.website.locale')
        self.ProductAttribute = POOL.get('product.attribute')
        self.ProductAttributeSet = POOL.get('product.attribute.set')
        self.VariationAttributes = POOL.get('product.variation_attributes')

    def test0010_product_variation_attributes(self):
        '''
        Test if product has all the attributes of variation_attributes.
        '''
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            uom, = self.Uom.search([], limit=1)

            # Create attributes
            attribute1, = self.ProductAttribute.create([{
                'name': 'size',
                'type_': 'selection',
                'string': 'Size',
                'selection': 'm: M\nl:L\nxl:XL'
            }])
            attribute2, = self.ProductAttribute.create([{
                'name': 'color',
                'type_': 'selection',
                'string': 'Color',
                'selection': 'blue: Blue\nblack:Black'
            }])
            attribute3, = self.ProductAttribute.create([{
                'name': 'attrib',
                'type_': 'char',
                'string': 'Attrib',
            }])
            attribute4, = self.ProductAttribute.create([{
                'name': 'ø',
                'type_': 'char',
                'string': 'ø',
            }])

            # Create attribute set
            attrib_set, = self.ProductAttributeSet.create([{
                'name': 'Cloth',
                'attributes': [
                    ('add', [attribute1.id, attribute2.id, attribute4.id])
                ]
            }])

            # Create product template with attribute set
            template1, = self.Template.create([{
                'name': 'THis is Product',
                'type': 'goods',
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'default_uom': uom.id,
                'attribute_set': attrib_set.id,
            }])

            # Create variation attributes
            self.VariationAttributes.create([{
                'template': template1.id,
                'attribute': attribute1.id,
            }, {
                'template': template1.id,
                'attribute': attribute2.id,
            }, {
                'template': template1.id,
                'attribute': attribute4.id,
            }])

            # Try to create product with no attributes
            with self.assertRaises(UserError):
                self.Product.create([{
                    'template': template1.id,
                    'displayed_on_eshop': True,
                    'uri': 'uri1',
                    'code': 'SomeProductCode',
                }])

            # Try to create product with only one attribute
            with self.assertRaises(UserError):
                self.Product.create([{
                    'template': template1.id,
                    'displayed_on_eshop': True,
                    'uri': 'uri2',
                    'code': 'SomeProductCode',
                    'attributes': {'color': 'blue'}
                }])

            # Finally create product with all attributes mentioned in
            # template variation_attributes.
            product1, = self.Product.create([{
                'template': template1.id,
                'displayed_on_eshop': True,
                'uri': 'uri3',
                'code': 'SomeProductCode',
                'attributes': {
                    'color': 'blue',
                    'size': 'L',
                    'ø': 'something'
                }
            }])
            self.assert_(product1)

    def test_0020_product_variation_data(self):
        """
        Test get_product_variation_data method.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            uom, = self.Uom.search([], limit=1)
            app = self.get_app()

            with app.test_request_context():
                # Create attributes
                attribute1, = self.ProductAttribute.create([{
                    'name': 'size',
                    'type_': 'selection',
                    'string': 'Size',
                    'selection': 'm: M\nl:L\nxl:XL'
                }])
                attribute2, = self.ProductAttribute.create([{
                    'name': 'color',
                    'type_': 'selection',
                    'string': 'Color',
                    'selection': 'blue: Blue\nblack:Black'
                }])

                # Create attribute set
                attrib_set, = self.ProductAttributeSet.create([{
                    'name': 'Cloth',
                    'attributes': [
                        ('add', [attribute1.id, attribute2.id])
                    ]
                }])

                # Create product template with attribute set
                template1, = self.Template.create([{
                    'name': 'THis is Product',
                    'type': 'goods',
                    'list_price': Decimal('10'),
                    'cost_price': Decimal('5'),
                    'default_uom': uom.id,
                    'attribute_set': attrib_set.id,
                }])

                # Create variation attributes
                self.VariationAttributes.create([{
                    'template': template1.id,
                    'attribute': attribute1.id,
                }, {
                    'template': template1.id,
                    'attribute': attribute2.id,
                }])

                product1, = self.Product.create([{
                    'template': template1.id,
                    'displayed_on_eshop': True,
                    'uri': 'uri3',
                    'code': 'SomeProductCode',
                    'attributes': {
                        'color': 'blue',
                        'size': 'L',
                        'ø': 'something'
                    }
                }])

                self.assertGreater(
                    len(template1.get_product_variation_data()), 0
                )


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
