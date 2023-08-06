# -*- coding: utf-8 -*-
"""
    country.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Country']
__metaclass__ = PoolMeta


class Country:
    'Country'
    __name__ = 'country.country'

    sequence = fields.Integer("Sequence", required=True)

    @classmethod
    def __setup__(cls):
        super(Country, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))
        cls._order.insert(1, ('name', 'ASC'))

    @staticmethod
    def default_sequence():
        return 300
