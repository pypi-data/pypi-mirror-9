# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from .sale import Sale, Configuration


def register():
    Pool.register(
        Sale,
        Configuration,
        module='sale_shipment_cost_cap', type_='model'
    )
