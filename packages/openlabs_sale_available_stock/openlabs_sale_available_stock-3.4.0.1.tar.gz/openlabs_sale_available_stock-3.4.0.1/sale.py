# -*- coding: utf-8 -*-
"""
    sale.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction
from trytond.pyson import Eval, Or

__metaclass__ = PoolMeta
__all__ = ['SaleLine']


class SaleLine:
    __name__ = 'sale.line'

    available_stock_qty = fields.Function(
        fields.Float(
            'Available Quantity',
            digits=(16, Eval('unit_digits', 2)),
            states={
                'invisible': Or(
                    Eval('type') != 'line',
                    Eval('sale_state') == 'done'
                ),
            },
            depends=['type', 'unit_digits', 'sale_state']
        ),
        'on_change_with_available_stock_qty'
    )

    sale_state = fields.Function(
        fields.Char('Sale State'), 'get_sale_state'
    )

    @fields.depends(
        '_parent_sale.warehouse', '_parent_sale.sale_date',
        'product', 'type')
    def on_change_with_available_stock_qty(self, name=None):
        """
        Returns the available stock to process a Sale
        """
        Location = Pool().get('stock.location')
        Date = Pool().get('ir.date')

        try:
            self.warehouse
        except AttributeError:
            # On change will not have the warehouse set since its constructed
            # from a dictionary of changes rather than the database active
            # record. The warehouse on line is never displayed on view and
            # won't be there.
            self.warehouse = Location(self.get_warehouse(None))

        # If a date is specified on sale, use that. If not, use the
        # current date.
        date = self.sale.sale_date or Date.today()

        # If the sales person is taking an order for a date in the past
        # (which tryton allows), the stock cannot be of the past, but of
        # the current date.
        date = max(date, Date.today())

        if self.type == 'line' and self.product and self.warehouse:
            with Transaction().set_context(
                    locations=[self.warehouse.id],  # warehouse of the line
                    stock_skip_warehouse=True,      # quantity of storage only
                    stock_date_end=date,            # Stock as of sale date
                    stock_assign=True):             # Exclude Assigned
                if date <= Date.today():
                    return self.product.quantity
                else:
                    # For a sale in the future, it is more interesting to
                    # see the forecasted quantity rather than what is
                    # currently in the warehouse.
                    return self.product.forecast_quantity

    def get_sale_state(self, name):
        """
        Returns the state of the Sale
        """
        return self.sale and self.sale.state
