# This file is part sale_invoice_grouping_shipment_party module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import (doctest_setup, doctest_teardown,
    doctest_checker)
from trytond.pool import Pool


class SaleInvoiceGroupingShipmentPartyTestCase(ModuleTestCase):
    'Test Sale Invoice Grouping Shipment Party module'
    module = 'sale_invoice_grouping_shipment_party'


    @with_transaction()
    def test_sale(self):
        'Create category'
        pool = Pool()
        Party = pool.get('party.party')
        Sale = pool.get('sale.sale')

        party1 = Party()
        party1.name = 'Party 1'
        party1.save()

        party2 = Party()
        party2.name = 'Party 2'
        party2.save()

        party3 = Party()
        party3.name = 'Party 3'
        party3.party_sale_payer = party2
        party3.save()

        sale = Sale()

        sale.shipment_party = party1
        sale.on_change_shipment_party()
        self.assertEqual(sale.party, party1)

        sale.shipment_party = party3
        sale.on_change_shipment_party()
        self.assertEqual(sale.party, party2)

        sale.shipment_party = party1
        sale.on_change_shipment_party()
        self.assertEqual(sale.party, party1)

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
