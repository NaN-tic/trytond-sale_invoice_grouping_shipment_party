
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.modules.company.tests import CompanyTestMixin


class SaleInvoiceGroupingShipmentPartyTestCase(CompanyTestMixin, ModuleTestCase):
    'Test SaleInvoiceGroupingShipmentParty module'
    module = 'sale_invoice_grouping_shipment_party'
    extras = ['sale_carrier',
              'account_invoice_discount_global',
              'sale_invoice_grouping_by_address'
              ]

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
        self.assertEqual(sale.party, party2)


del ModuleTestCase
