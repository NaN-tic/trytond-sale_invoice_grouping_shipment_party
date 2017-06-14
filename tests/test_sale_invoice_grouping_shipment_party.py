# This file is part sale_invoice_grouping_shipment_party module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import (doctest_setup, doctest_teardown,
    doctest_checker)

class SaleInvoiceGroupingShipmentPartyTestCase(ModuleTestCase):
    'Test Sale Invoice Grouping Shipment Party module'
    module = 'sale_invoice_grouping_shipment_party'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            SaleInvoiceGroupingShipmentPartyTestCase))
    suite.addTests(doctest.DocFileSuite(
            'scenario_sale_invoice_grouping_shipment_party.rst',
            setUp=doctest_setup, tearDown=doctest_teardown, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
            checker=doctest_checker))
    return suite
