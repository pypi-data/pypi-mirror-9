# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from product import Template, Product, ProductVariationAttributes, \
    ProductAttribute


def register():
    Pool.register(
        Template,
        Product,
        ProductVariationAttributes,
        ProductAttribute,
        module='nereid_catalog_variants', type_='model'
    )
