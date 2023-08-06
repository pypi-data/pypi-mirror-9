# -*- coding: utf-8 -*-
"""

    invoice

    :copyright: (c) 2014-2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta, Pool
from trytond.exceptions import UserError
from trytond.model import fields, ModelView
from trytond.pyson import Eval, Bool, And, Or, Id, Not
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button

from trytond.modules.payment_gateway.transaction import BaseCreditCardViewMixin

__all__ = [
    'Invoice', 'PayInvoiceUsingTransactionStart', 'PayInvoiceUsingTransaction',
    'PaymentTransaction'
]
__metaclass__ = PoolMeta


class Invoice:
    __name__ = 'account.invoice'

    @classmethod
    def __setup__(cls):
        super(Invoice, cls).__setup__()
        cls._buttons.update({
            'pay_using_payment_transaction': {
                'invisible': Eval('state') != 'posted',
                'readonly': ~Eval('groups', []).contains(
                    Id('account', 'group_account')),
            },
        })

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

    @classmethod
    @ModelView.button_action(
        'invoice_payment_gateway.wizard_pay_using_transaction')
    def pay_using_payment_transaction(cls, invoices):  # pragma: no cover
        pass


class PayInvoiceUsingTransactionStart(BaseCreditCardViewMixin, ModelView):
    'Pay using Transaction Wizard'
    __name__ = 'account.invoice.pay_using_transaction.start'

    invoice = fields.Many2One(
        'account.invoice', 'Invoice', required=True, readonly=True
    )
    party = fields.Many2One('party.party', 'Party', readonly=True)
    gateway = fields.Many2One(
        'payment_gateway.gateway', 'Gateway', required=True,
        domain=[('users', '=', Eval('user'))],
        depends=['user']
    )
    method = fields.Function(
        fields.Char('Payment Gateway Method'), 'get_method'
    )
    use_existing_card = fields.Boolean(
        'Use existing Card?', states={
            'invisible': Eval('method') != 'credit_card'
        }, depends=['method']
    )
    payment_profile = fields.Many2One(
        'party.payment_profile', 'Payment Profile',
        domain=[
            ('party', '=', Eval('party')),
            ('gateway', '=', Eval('gateway')),
        ],
        states={
            'required': And(
                Eval('method') == 'credit_card', Bool(Eval('use_existing_card'))
            ),
            'invisible': ~Bool(Eval('use_existing_card'))
        }, depends=['method', 'use_existing_card', 'party', 'gateway']
    )
    user = fields.Many2One(
        "res.user", "Tryton User", readonly=True
    )
    amount = fields.Numeric(
        'Amount', digits=(16, Eval('currency_digits', 2)),
        required=True, depends=['currency_digits'],
    )
    currency_digits = fields.Function(
        fields.Integer('Currency Digits'),
        'get_currency_digits'
    )
    reference = fields.Char(
        'Reference', states={
            'invisible': Not(Eval('method') == 'manual'),
        }
    )

    @classmethod
    def __setup__(cls):
        super(PayInvoiceUsingTransactionStart, cls).__setup__()

        INV = Or(
            Eval('method') == 'manual',
            And(
                Eval('method') == 'credit_card',
                Bool(Eval('use_existing_card'))
            )
        )
        STATE1 = {
            'required': And(
                ~Bool(Eval('use_existing_card')),
                Eval('method') == 'credit_card'
            ),
            'invisible': INV
        }
        DEPENDS = ['use_existing_card', 'method']

        cls.owner.states.update(STATE1)
        cls.owner.depends.extend(DEPENDS)
        cls.number.states.update(STATE1)
        cls.number.depends.extend(DEPENDS)
        cls.expiry_month.states.update(STATE1)
        cls.expiry_month.depends.extend(DEPENDS)
        cls.expiry_year.states.update(STATE1)
        cls.expiry_year.depends.extend(DEPENDS)
        cls.csc.states.update(STATE1)
        cls.csc.depends.extend(DEPENDS)
        cls.swipe_data.states = {'invisible': INV}
        cls.swipe_data.depends = ['method']

    def get_currency_digits(self, name):  # pragma: no cover
        return self.invoice.currency_digits if self.invoice else 2

    def get_method(self, name=None):  # pragma: no cover
        """
        Return the method based on the gateway
        """
        return self.gateway.method

    @fields.depends('gateway')
    def on_change_gateway(self):  # pragma: no cover
        if self.gateway:
            return {
                'method': self.gateway.method,
            }
        return {}


class PayInvoiceUsingTransaction(Wizard):
    'Pay using Transaction Wizard'
    __name__ = 'account.invoice.pay_using_transaction'

    start = StateView(
        'account.invoice.pay_using_transaction.start',
        'invoice_payment_gateway.pay_using_transaction_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Ok', 'pay', 'tryton-ok', default=True),
        ]
    )
    pay = StateTransition()

    def default_start(self, field=None):
        Invoice = Pool().get('account.invoice')

        invoice = Invoice(Transaction().context.get('active_id'))

        res = {
            'invoice': invoice.id,
            'party': invoice.party.id,
            'owner': invoice.party.name,
            'currency_digits': invoice.currency_digits,
            'amount': invoice.amount_to_pay_today or invoice.amount_to_pay,
            'user': Transaction().user,
        }
        return res

    def create_payment_transaction(self, profile=None):
        """
        Helper function to create new payment transaction
        """
        PaymentTransaction = Pool().get('payment_gateway.transaction')
        Date = Pool().get('ir.date')

        return PaymentTransaction(
            origin='%s,%s' % (
                self.start.invoice.__name__, self.start.invoice.id),
            party=self.start.party,
            address=self.start.invoice.invoice_address,
            gateway=self.start.gateway,
            payment_profile=profile,
            amount=self.start.amount,
            description=self.start.reference or None,
            date=Date.today(),
        )

    def create_payment_profile(self):
        """
        Helper function to create payment profile
        """
        Invoice = Pool().get('account.invoice')
        ProfileWizard = Pool().get(
            'party.party.payment_profile.add', type="wizard"
        )
        profile_wizard = ProfileWizard(
            ProfileWizard.create()[0]
        )
        profile_wizard.card_info.owner = self.start.owner
        profile_wizard.card_info.number = self.start.number
        profile_wizard.card_info.expiry_month = self.start.expiry_month
        profile_wizard.card_info.expiry_year = self.start.expiry_year
        profile_wizard.card_info.csc = self.start.csc or ''
        profile_wizard.card_info.gateway = self.start.gateway
        profile_wizard.card_info.provider = self.start.gateway.provider
        profile_wizard.card_info.address = Invoice(
            Transaction().context.get('active_id')
        ).invoice_address
        profile_wizard.card_info.party = self.start.party

        with Transaction().set_context(return_profile=True):
            profile = profile_wizard.transition_add()
        return profile

    def transition_pay(self):
        """
        Creates a new payment transaction and pay invoice with it
        """
        PaymentTransaction = Pool().get('payment_gateway.transaction')

        profile = self.start.payment_profile
        if self.start.method == 'credit_card' and (
            not self.start.use_existing_card
        ):
            profile = self.create_payment_profile()

        transaction = self.create_payment_transaction(profile=profile)
        transaction.save()

        # Capture Transaction
        PaymentTransaction.capture([transaction])
        # Pay invoice using above captured transaction
        self.start.invoice.pay_using_transaction(transaction)
        return 'end'


class PaymentTransaction:
    'Gateway Transaction'
    __name__ = 'payment_gateway.transaction'

    @classmethod
    def _get_origin(cls):
        'Add invoice to the selections'
        res = super(PaymentTransaction, cls)._get_origin()

        res.append('account.invoice')
        return res
