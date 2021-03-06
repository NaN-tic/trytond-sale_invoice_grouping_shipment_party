# This file is part sale_invoice_grouping_shipment_party module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import carrier
from . import invoice
from . import sale
from . import party

def register():
    Pool.register(
        invoice.Invoice,
        sale.Sale,
        party.Party,
        module='sale_invoice_grouping_shipment_party', type_='model')
    Pool.register(
        carrier.Sale,
        carrier.Configuration,
        carrier.ConfigurationCarrier,
        depends=['sale_carrier'],
        module='sale_invoice_grouping_shipment_party', type_='model')
