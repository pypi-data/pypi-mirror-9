# -*- coding: utf-8 -*-
"""
    __init__

    :copyright: (c) 2014-2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from invoice import Invoice, PayInvoiceUsingTransactionStart, \
    PayInvoiceUsingTransaction, PaymentTransaction


def register():
    Pool.register(
        Invoice,
        PaymentTransaction,
        PayInvoiceUsingTransactionStart,
        module='invoice_payment_gateway', type_='model'
    )
    Pool.register(
        PayInvoiceUsingTransaction,
        module='invoice_payment_gateway', type_='wizard'
    )
