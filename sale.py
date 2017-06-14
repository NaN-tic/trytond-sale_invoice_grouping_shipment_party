# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta

__all__ = ['Sale']


class Sale:
    __metaclass__ = PoolMeta
    __name__ = 'sale.sale'

    @property
    def _invoice_grouping_fields(self):
        return super(Sale, self)._invoice_grouping_fields + ('shipment_party',)

    def _get_grouped_invoice_domain(self, invoice):
        invoice_domain = super(Sale, self)._get_grouped_invoice_domain(invoice)
        if self.shipment_party:
            invoice_domain[
                invoice_domain.index(('shipment_party', '=', None))
                ] = ('shipment_party', '=', self.shipment_party)
        return invoice_domain

    def _get_invoice_sale(self):
        invoice = super(Sale, self)._get_invoice_sale()
        if not hasattr(invoice, 'shipment_party') and self.shipment_party:
            invoice.shipment_party = self.shipment_party
        return invoice
