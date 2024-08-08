import unittest
from decimal import Decimal

from proteus import Model, Wizard
from trytond.exceptions import UserError
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import (
    create_payment_term, set_fiscalyear_invoice_sequences)
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install sale_invoice_grouping_shipment_party
        activate_modules('sale_invoice_grouping_shipment_party')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create payment term
        payment_term = create_payment_term()
        payment_term.save()

        # Create parties
        Party = Model.get('party.party')
        customer = Party(name='Customer')
        customer.sale_invoice_grouping_method = 'standard'
        customer.save()
        shipment_party = Party(name='Shipment Party')
        shipment_party.party_sale_payer = customer
        shipment_party.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        Product = Model.get('product.product')
        product = Product()
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.account_category = account_category
        template.save()
        product.template = template
        product.save()

        # Check we cannot save a sale with party payer configured
        Sale = Model.get('sale.sale')
        sale = Sale()
        sale.shipment_party = customer
        sale.party = shipment_party
        sale.invoice_method = 'order'

        with self.assertRaises(UserError):
            sale.save()

        # Check restoring the shipment_party, the party updates and the sale is allowed
        sale.shipment_party = shipment_party
        sale.payment_term = payment_term
        self.assertEqual(sale.party.name, 'Customer')

        sale_line = sale.lines.new()
        sale_line.product = product
        sale_line.quantity = 2.0
        sale.click('quote')
        sale.click('confirm')
        sale.click('process')
        self.assertEqual(sale.state, 'processing')

        invoice, = sale.invoices
        self.assertEqual(invoice.shipment_party, shipment_party)
        self.assertEqual(invoice.party, customer)
        self.assertEqual(len(invoice.lines), 1)

        sale = Sale()
        sale.party = customer
        sale.shipment_party = shipment_party
        sale.invoice_method = 'order'
        sale.payment_term = payment_term
        sale_line = sale.lines.new()
        sale_line.product = product
        sale_line.quantity = 2.0
        sale.click('quote')
        sale.click('confirm')
        sale.click('process')
        self.assertEqual(sale.state, 'processing')

        invoice, = sale.invoices
        self.assertEqual(invoice.shipment_party, shipment_party)
        self.assertEqual(invoice.party, customer)
        self.assertEqual(len(invoice.lines), 2)

        # Two sales without shipment party
        sale = Sale()
        sale.party = customer
        sale.shipment_party = None
        sale.invoice_method = 'order'
        sale.payment_term = payment_term
        sale_line = sale.lines.new()
        sale_line.product = product
        sale_line.quantity = 2.0
        sale.click('quote')
        sale.click('confirm')
        sale.click('process')
        self.assertEqual(sale.state, 'processing')

        invoice, = sale.invoices
        self.assertEqual(invoice.shipment_party, None)
        self.assertEqual(invoice.party, customer)
        self.assertEqual(len(invoice.lines), 1)

        sale = Sale()
        sale.party = customer
        sale.shipment_party = None
        sale.invoice_method = 'order'
        sale.payment_term = payment_term
        sale_line = sale.lines.new()
        sale_line.product = product
        sale_line.quantity = 2.0
        sale.click('quote')
        sale.click('confirm')
        sale.click('process')
        self.assertEqual(sale.state, 'processing')

        invoice, = sale.invoices
        self.assertEqual(invoice.shipment_party, None)
        self.assertEqual(invoice.party, customer)
        self.assertEqual(len(invoice.lines), 2)

        invoice.click('post')
        self.assertEqual(invoice.state, 'posted')

        # Credit invoice with refund
        credit = Wizard('account.invoice.credit', [invoice])
        credit.form.with_refund = True
        credit.form.invoice_date = invoice.invoice_date
        credit.execute('credit')
        invoice.reload()
        self.assertEqual(invoice.state, 'cancelled')

        # Check we cannot save an invoice with party payer configured
        Invoice = Model.get('account.invoice')
        invoice = Invoice()
        invoice.shipment_party = customer
        invoice.party = shipment_party
        invoice.payment_term = payment_term

        with self.assertRaises(UserError):
            invoice.save()

        # Ensure that changing the shipment_party updates the party and
        # the invoice can be saved
        invoice.shipment_party = shipment_party
        self.assertEqual(invoice.party.name, 'Customer')
        invoice.save()
