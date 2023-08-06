# -*- coding: utf-8 -*-
"""
    product.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval, Bool, Not

__all__ = ['Product']

__metaclass__ = PoolMeta


class Product:
    "Product"

    __name__ = 'product.product'

    customs_value = fields.Numeric(
        "Customs Value",
        states={
            'invisible': Bool(Eval('use_list_price_as_customs_value')),
            'required': Not(Bool(Eval('use_list_price_as_customs_value')))
        }, depends=['use_list_price_as_customs_value'],
    )

    use_list_price_as_customs_value = fields.Boolean(
        "Use List Price As Customs Value ?"
    )

    customs_value_used = fields.Function(
        fields.Numeric("Customs Value Used"),
        'get_customs_value_used'
    )

    @staticmethod
    def default_use_list_price_as_customs_value():
        return True

    def get_customs_value_used(self, name):
        if self.use_list_price_as_customs_value:
            return self.list_price
        return self.customs_value
