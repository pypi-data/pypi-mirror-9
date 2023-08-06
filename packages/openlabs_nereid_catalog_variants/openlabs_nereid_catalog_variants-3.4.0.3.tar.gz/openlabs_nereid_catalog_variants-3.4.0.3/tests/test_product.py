# -*- coding: utf-8 -*-
"""
    tests/test_product.py

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
import json
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from nereid.testing import NereidTestCase
from trytond.transaction import Transaction
from trytond.exceptions import UserError

from trytond.config import config
config.set('database', 'path', '/tmp')


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
        en_us, = self.Language.search([('code', '=', 'en_US')])

        self.locale_en_us, = self.Locale.create([{
            'code': 'en_US',
            'language': en_us.id,
            'currency': usd.id,
        }])
        self.NereidWebsite.create([{
            'name': 'localhost',
            'company': company.id,
            'application_user': USER,
            'default_locale': self.locale_en_us.id,
            'currencies': [('add', [usd.id])],
        }])

    def create_static_file(self, file_buffer, folder_name):
        """
        Creates the static file for testing
        """
        folder, = self.StaticFolder.create([{
            'folder_name': folder_name,
            'description': 'Test Folder'
        }])

        return self.StaticFile.create([{
            'name': 'test.png',
            'folder': folder.id,
            'file_binary': file_buffer,
        }])[0]

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
        self.Language = POOL.get('ir.lang')
        self.NereidWebsite = POOL.get('nereid.website')
        self.Party = POOL.get('party.party')
        self.Template = POOL.get('product.template')
        self.Uom = POOL.get('product.uom')
        self.Locale = POOL.get('nereid.website.locale')
        self.ProductAttribute = POOL.get('product.attribute')
        self.ProductAttributeSet = POOL.get('product.attribute.set')
        self.VariationAttributes = POOL.get('product.variation_attributes')
        self.StaticFolder = POOL.get("nereid.static.folder")
        self.StaticFile = POOL.get("nereid.static.file")

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
                'display_name': 'Size',
                'selection': [
                    ('create', [{
                        'name': 'm',
                    }, {
                        'name': 'l',
                    }, {
                        'name': 'xl',
                    }])
                ]
            }])
            attribute2, = self.ProductAttribute.create([{
                'name': 'color',
                'type_': 'selection',
                'selection': [
                    ('create', [{
                        'name': 'blue',
                    }, {
                        'name': 'black',
                    }])
                ]
            }])
            attribute3, = self.ProductAttribute.create([{
                'name': 'attrib',
                'type_': 'char',
                'display_name': 'Attrib',
            }])
            attribute4, = self.ProductAttribute.create([{
                'name': 'ø',
                'type_': 'char',
                'display_name': 'ø',
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
                    'attributes': [
                        ('create', [{
                            'attribute': attribute2.id,
                            'value_selection': attribute2.selection[0].id,
                        }])
                    ],
                }])

            # Finally create product with all attributes mentioned in
            # template variation_attributes.
            product1, = self.Product.create([{
                'template': template1.id,
                'displayed_on_eshop': True,
                'uri': 'uri3',
                'code': 'SomeProductCode',
                'attributes': [
                    ('create', [{
                        'attribute': attribute1.id,
                        'value_selection': attribute1.selection[1].id,
                    }, {
                        'attribute': attribute2.id,
                        'value_selection': attribute2.selection[0].id,
                    }, {
                        'attribute': attribute4.id,
                        'value_char': 'Test Char Value',
                    }])
                ],
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
                    'display_name': 'Size',
                    'selection': [
                        ('create', [{
                            'name': 'm',
                        }, {
                            'name': 'l',
                        }, {
                            'name': 'xl',
                        }])
                    ]
                }])
                attribute2, = self.ProductAttribute.create([{
                    'name': 'color',
                    'type_': 'selection',
                    'selection': [
                        ('create', [{
                            'name': 'blue',
                        }, {
                            'name': 'black',
                        }])
                    ]
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
                    'attributes': [
                        ('create', [{
                            'attribute': attribute1.id,
                            'value_selection': attribute1.selection[1].id,
                        }, {
                            'attribute': attribute2.id,
                            'value_selection': attribute2.selection[0].id,
                        }])
                    ],
                }])

                self.assertGreater(
                    len(template1.get_product_variation_data()), 0
                )

    def test_0030_product_variation_data_images(self):
        """
        Test get_product_variation_data method for images.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            uom, = self.Uom.search([], limit=1)
            file1 = self.create_static_file(buffer('test'), 'test')
            file2 = self.create_static_file(buffer('test-again'), 'test-again')
            app = self.get_app()

            product_template, = self.Template.create([{
                'name': 'test template',
                'type': 'goods',
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'default_uom': uom.id,
                'description': 'Description of template',
                'products': [('create', self.Template.default_products())],
                'media': [('create', [{
                    'static_file': file1.id,
                }])],
            }])

            product, = product_template.products

            self.Product.write([product], {
                'displayed_on_eshop': True,
                'uri': 'uri1',
                'media': [('create', [{
                    'static_file': file2.id,
                }])],
            })

            with app.test_request_context('/'):
                res = json.loads(product.get_product_variation_data())
                self.assertGreater(res, 0)

                self.assertFalse(
                    res['variants'][0]['image_urls'][0]['thumbnail']
                    is None
                )
                self.assertFalse(
                    res['variants'][0]['image_urls'][0]['large']
                    is None
                )
                self.assertEqual(
                    res['variants'][0]['rec_name'], product.rec_name
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
