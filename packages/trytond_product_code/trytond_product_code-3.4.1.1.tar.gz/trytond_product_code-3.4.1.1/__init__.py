# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from product import (Product, ProductCode)


def register():
    Pool.register(
        Product,
        ProductCode,
        module='product_code', type_='model')
