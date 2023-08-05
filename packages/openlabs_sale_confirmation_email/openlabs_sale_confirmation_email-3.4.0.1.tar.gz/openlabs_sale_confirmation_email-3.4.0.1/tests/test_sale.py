# -*- coding: utf-8 -*-
"""
    tests/test_product.py
    :copyright: (C) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from trytond.transaction import Transaction
from trytond.pyson import Eval
from trytond.config import config

config.set('email', 'from', 'umang.arora@openlabs.co.in')


class TestSale(unittest.TestCase):

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('sale_confirmation_email')

        self.Currency = POOL.get('currency.currency')
        self.Company = POOL.get('company.company')
        self.Party = POOL.get('party.party')
        self.User = POOL.get('res.user')
        self.ProductTemplate = POOL.get('product.template')
        self.Uom = POOL.get('product.uom')
        self.ProductCategory = POOL.get('product.category')
        self.Product = POOL.get('product.product')
        self.Country = POOL.get('country.country')
        self.Subdivision = POOL.get('country.subdivision')
        self.Journal = POOL.get('account.journal')
        self.Sale = POOL.get('sale.sale')
        self.SaleLine = POOL.get('sale.line')

    def _create_fiscal_year(self, date=None, company=None):
        """
        Creates a fiscal year and requried sequences
        """
        FiscalYear = POOL.get('account.fiscalyear')
        Sequence = POOL.get('ir.sequence')
        SequenceStrict = POOL.get('ir.sequence.strict')
        Company = POOL.get('company.company')

        if date is None:
            date = datetime.date.today()

        if company is None:
            company, = Company.search([], limit=1)

        invoice_sequence, = SequenceStrict.create([{
            'name': '%s' % date.year,
            'code': 'account.invoice',
            'company': company,
        }])
        fiscal_year, = FiscalYear.create([{
            'name': '%s' % date.year,
            'start_date': date + relativedelta(month=1, day=1),
            'end_date': date + relativedelta(month=12, day=31),
            'company': company,
            'post_move_sequence': Sequence.create([{
                'name': '%s' % date.year,
                'code': 'account.move',
                'company': company,
            }])[0],
            'out_invoice_sequence': invoice_sequence,
            'in_invoice_sequence': invoice_sequence,
            'out_credit_note_sequence': invoice_sequence,
            'in_credit_note_sequence': invoice_sequence,
        }])
        FiscalYear.create_period([fiscal_year])
        return fiscal_year

    def _create_coa_minimal(self, company):
        """Create a minimal chart of accounts
        """
        AccountTemplate = POOL.get('account.account.template')
        Account = POOL.get('account.account')

        account_create_chart = POOL.get(
            'account.create_chart', type="wizard")

        account_template, = AccountTemplate.search(
            [('parent', '=', None)]
        )

        session_id, _, _ = account_create_chart.create()
        create_chart = account_create_chart(session_id)
        create_chart.account.account_template = account_template
        create_chart.account.company = company
        create_chart.transition_create_account()

        receivable, = Account.search([
            ('kind', '=', 'receivable'),
            ('company', '=', company),
        ])
        payable, = Account.search([
            ('kind', '=', 'payable'),
            ('company', '=', company),
        ])
        create_chart.properties.company = company
        create_chart.properties.account_receivable = receivable
        create_chart.properties.account_payable = payable
        create_chart.transition_create_properties()

    def _get_account_by_kind(self, kind, company=None, silent=True):
        """Returns an account with given spec
        :param kind: receivable/payable/expense/revenue
        :param silent: dont raise error if account is not found
        """
        Account = POOL.get('account.account')
        Company = POOL.get('company.company')

        if company is None:
            company, = Company.search([], limit=1)

        accounts = Account.search([
            ('kind', '=', kind),
            ('company', '=', company)
        ], limit=1)
        if not accounts and not silent:
            raise Exception("Account not found")
        return accounts[0] if accounts else False

    def _create_payment_term(self):
        """Create a simple payment term with all advance
        """
        PaymentTerm = POOL.get('account.invoice.payment_term')

        return PaymentTerm.create([{
            'name': 'Direct',
            'lines': [('create', [{'type': 'remainder'}])]
        }])

    def setup_defaults(self):
        """Creates default data for testing
        """
        self.country, = self.Country.create([{
            'name': 'United States of America',
            'code': 'US',
        }])
        self.subdivision, = self.Subdivision.create([{
            'country': self.country.id,
            'name': 'California',
            'code': 'CA',
            'type': 'state',
        }])

        self.currency, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])

        with Transaction().set_context(company=None):
            company_party, = self.Party.create([{
                'name': 'openlabs'
            }])

        self.company, = self.Company.create([{
            'party': company_party,
            'currency': self.currency,
        }])

        self.User.write([self.User(USER)], {
            'company': self.company,
            'main_company': self.company,
        })
        CONTEXT.update(self.User.get_preferences(context_only=True))

        # Create Fiscal Year
        self._create_fiscal_year(company=self.company.id)
        # Create Chart of Accounts
        self._create_coa_minimal(company=self.company.id)
        # Create a payment term
        self.payment_term, = self._create_payment_term()

        self.cash_journal, = self.Journal.search(
            [('type', '=', 'cash')], limit=1
        )
        self.Journal.write([self.cash_journal], {
            'debit_account': self._get_account_by_kind('other').id
        })

        # Create party
        self.party, = self.Party.create([{
            'name': 'Bruce Wayne',
            'addresses': [('create', [{
                'name': 'Bruce Wayne',
                'party': Eval('id'),
                'city': 'Gotham',
                'invoice': True,
                'country': self.country.id,
                'subdivision': self.subdivision.id,
            }])],
            'customer_payment_term': self.payment_term.id,
            'account_receivable': self._get_account_by_kind(
                'receivable').id,
            'contact_mechanisms': [('create', [
                {'type': 'email', 'value': 'ua@ol.in'},
            ])],
        }])

        self.uom, = self.Uom.search([('name', '=', 'Unit')])
        self.product_category, = self.ProductCategory.create([{
            'name': 'Automobile',
            'account_revenue': self._get_account_by_kind(
                'revenue', company=self.company.id).id,
            'account_expense': self._get_account_by_kind(
                'expense', company=self.company.id).id,
        }])

        self.product_template, = self.ProductTemplate.create([{
            'name': 'Bat Mobile',
            'type': 'goods',
            'salable': True,
            'category': self.product_category.id,
            'default_uom': self.uom.id,
            'sale_uom': self.uom.id,
            'list_price': Decimal('20000'),
            'cost_price': Decimal('15000'),
            'account_category': True,
        }])

        self.product, = self.Product.create([{
            'template': self.product_template.id,
            'code': '123',
        }])

    def test_0010_test_email_on_confirm(self):
        """
        Test if an email is sent when sale is confirmed
        """
        Date = POOL.get('ir.date')
        EmailQueue = POOL.get('email.queue')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            sale, = self.Sale.create([{
                'reference': 'Test Sale',
                'payment_term': self.payment_term.id,
                'currency': self.company.currency.id,
                'party': self.party.id,
                'invoice_address': self.party.addresses[0].id,
                'shipment_address': self.party.addresses[0].id,
                'sale_date': Date.today(),
                'company': self.company.id,
            }])
            sale_line, = self.SaleLine.create([{
                'sale': sale,
                'type': 'line',
                'quantity': 2,
                'unit': self.uom,
                'unit_price': 20000,
                'description': 'Test description',
                'product': self.product.id
            }])

            self.Sale.quote([sale])
            self.assertEqual(len(EmailQueue.search([])), 0)

            # Confirm Sale
            self.Sale.confirm([sale])

            emails = EmailQueue.search([])
            self.assertEqual(len(emails), 1)
            self.assertEqual(emails[0].to_addrs, self.party.email)
            self.assertNotEqual(
                emails[0].msg.find(self.party.email), -1
            )
            self.assertNotEqual(
                emails[0].msg.find(config.get('email', 'from')), -1
            )
            self.assertNotEqual(
                emails[0].msg.find('Order Confirmed'), -1
            )
            self.assertTrue(sale.email_sent)
            # Try sending email for same sale and test if email is
            # not sent again
            sale.send_confirmation_email()
            self.assertEqual(len(EmailQueue.search([])), 1)


def suite():
    "Define suite"
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestSale)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
