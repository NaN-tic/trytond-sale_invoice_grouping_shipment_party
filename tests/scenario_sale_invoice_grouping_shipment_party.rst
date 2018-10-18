=============================================
Sale Invoice Grouping Shipment Party Scenario
=============================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()
    >>> start_month = today + relativedelta(day=1)
    >>> same_biweekly = today + relativedelta(day=10)
    >>> next_biweekly = today + relativedelta(day=20)
    >>> next_month = today + relativedelta(months=1)

Install sale_invoice_grouping_shipment_party::

    >>> config = activate_modules('sale_invoice_grouping_shipment_party')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create parties::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.sale_invoice_grouping_method = 'standard'
    >>> customer.save()
    >>> shipment_party = Party(name='Shipment Party')
    >>> shipment_party.party_sale_payer = customer
    >>> shipment_party.save()

Create account category::

    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = expense
    >>> account_category.account_revenue = revenue
    >>> account_category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.purchasable = True
    >>> template.salable = True
    >>> template.list_price = Decimal('10')
    >>> template.account_category = account_category
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Check we cannot save a sale with party payer configured::

    >>> Sale = Model.get('sale.sale')
    >>> sale = Sale()
    >>> sale.shipment_party = customer
    >>> sale.party = shipment_party
    >>> sale.invoice_method = 'order'
    >>> sale.payment_term = payment_term
    >>> sale.save()   # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    UserError: ...

Check restoring the shipment_party, the party updates and the sale is allowed::

    >>> sale.shipment_party = shipment_party
    >>> sale.party.name
    'Customer'
    >>> sale_line = sale.lines.new()
    >>> sale_line.product = product
    >>> sale_line.quantity = 2.0
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> sale.state
    'processing'
    >>> invoice, = sale.invoices
    >>> invoice.shipment_party == shipment_party
    True
    >>> invoice.party == customer
    True
    >>> len(invoice.lines)
    1

    >>> sale = Sale()
    >>> sale.party = customer
    >>> sale.shipment_party = shipment_party
    >>> sale.invoice_method = 'order'
    >>> sale.payment_term = payment_term
    >>> sale_line = sale.lines.new()
    >>> sale_line.product = product
    >>> sale_line.quantity = 2.0
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> sale.state
    'processing'
    >>> invoice, = sale.invoices
    >>> invoice.shipment_party == shipment_party
    True
    >>> invoice.party == customer
    True
    >>> len(invoice.lines)
    2

Two sales without shipment party::

    >>> sale = Sale()
    >>> sale.party = customer
    >>> sale.shipment_party = None
    >>> sale.invoice_method = 'order'
    >>> sale.payment_term = payment_term
    >>> sale_line = sale.lines.new()
    >>> sale_line.product = product
    >>> sale_line.quantity = 2.0
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> sale.state
    'processing'
    >>> invoice, = sale.invoices
    >>> invoice.shipment_party == None
    True
    >>> invoice.party == customer
    True
    >>> len(invoice.lines)
    1

    >>> sale = Sale()
    >>> sale.party = customer
    >>> sale.shipment_party = None
    >>> sale.invoice_method = 'order'
    >>> sale.payment_term = payment_term
    >>> sale_line = sale.lines.new()
    >>> sale_line.product = product
    >>> sale_line.quantity = 2.0
    >>> sale.click('quote')
    >>> sale.click('confirm')
    >>> sale.click('process')
    >>> sale.state
    'processing'
    >>> invoice, = sale.invoices
    >>> invoice.shipment_party == None
    True
    >>> invoice.party == customer
    True
    >>> len(invoice.lines)
    2

Check we cannot save an invoice with party payer configured::

    >>> Invoice = Model.get('account.invoice')
    >>> invoice = Invoice()
    >>> invoice.shipment_party = customer
    >>> invoice.party = shipment_party
    >>> invoice.invoice_method = 'order'
    >>> invoice.payment_term = payment_term
    >>> invoice.save()   # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    UserError: ...

Ensure that changing the shipment_party updates the party and
the invoice can be saved::

    >>> invoice.shipment_party = shipment_party
    >>> invoice.party.name
    'Customer'
    >>> invoice.save()
