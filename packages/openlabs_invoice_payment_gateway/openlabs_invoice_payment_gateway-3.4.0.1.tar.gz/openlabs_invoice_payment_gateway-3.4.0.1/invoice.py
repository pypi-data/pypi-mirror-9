# -*- coding: utf-8 -*-
"""

    invoice

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta, Pool
from trytond.exceptions import UserError

__all__ = ['Invoice']
__metaclass__ = PoolMeta


class Invoice:
    __name__ = 'account.invoice'

    def pay_using_transaction(self, payment_transaction):
        """
        Pay an invoice using an existing payment_transaction

        :param payment_transaction: Active record of a payment transaction
        """
        AccountMoveLine = Pool().get('account.move.line')

        for line in payment_transaction.move.lines:
            if line.account == self.account:
                self.write(
                    [self], {'payment_lines': [('add', [line.id])]}
                )
                if self.amount_to_pay == 0:
                    # Reconcile lines to pay and payment lines from transaction
                    try:
                        AccountMoveLine.reconcile(
                            self.lines_to_pay + self.payment_lines
                        )
                    except UserError:
                        # If reconcilation fails, do not raise the error
                        pass
                return line
        raise Exception('Missing account')
