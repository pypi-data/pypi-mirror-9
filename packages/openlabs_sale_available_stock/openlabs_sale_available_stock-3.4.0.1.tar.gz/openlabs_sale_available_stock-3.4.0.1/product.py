# -*- coding: utf-8 -*-
"""
    product.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pyson import PYSONEncoder, PYSONDecoder
from trytond.modules.stock import ProductByLocation

__all__ = ['ProductByLocationExcludeAssigned']


class ProductByLocationExcludeAssigned(ProductByLocation):
    """
    Show Product by Locations excluding assigned quantities
    """
    __name__ = 'product.by_location.exclude_assigned'

    def do_open(self, action):
        action, data = super(
            ProductByLocationExcludeAssigned, self
        ).do_open(action)
        # Decode pyson context
        context = PYSONDecoder().decode(action['pyson_context'])
        # Update context
        context['stock_assign'] = True
        # Encode the new context to create new pyson context
        action['pyson_context'] = PYSONEncoder().encode(context)
        return action, data
