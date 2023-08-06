# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from sale import SaleLine
from product import ProductByLocationExcludeAssigned


def register():
    Pool.register(
        SaleLine,
        module='sale_available_stock', type_='model'
    )
    Pool.register(
        ProductByLocationExcludeAssigned,
        module='sale_available_stock', type_='wizard'
    )
