# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from sale import Sale


def register():
    Pool.register(
        Sale,
        module='sale_confirmation_email', type_='model'
    )
