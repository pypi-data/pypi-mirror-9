# -*- coding: utf-8 -*-
"""
    __init__

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from invoice import Invoice


def register():
    Pool.register(
        Invoice,
        module='invoice_payment_gateway', type_='model'
    )
