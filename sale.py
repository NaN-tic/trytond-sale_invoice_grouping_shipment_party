# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta

__all__ = ['Sale']


class Sale:
    __metaclass__ = PoolMeta
    __name__ = 'sale.sale'

    @classmethod
    def __setup__(cls):
        super(Sale,cls).__setup__()
        cls._error_messages.update({
                'error_party_payer': ('Party "%s" cannot be used as a payer'
                    ' because it has a payer defined'),
                })

    @classmethod
    def validate(cls, sales):
        super(Sale, cls).validate(sales)
        for sale in sales:
            sale.check_shipment_party()

    def check_shipment_party(self):
        if self.party.party_sale_payer:
            self.raise_user_error('error_party_payer', self.party.rec_name)

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

    def _get_invoice_sale(self, invoice_type):
        invoice = super(Sale, self)._get_invoice_sale(invoice_type)
        if not hasattr(invoice, 'shipment_party') and self.shipment_party:
            invoice.shipment_party = self.shipment_party
        return invoice

    def on_change_shipment_party(self):
        super(Sale, self).on_change_shipment_party()
        if self.shipment_party:
            if self.shipment_party.party_sale_payer:
                self.party = self.shipment_party.party_sale_payer
            else:
                self.party = self.shipment_party
            self.on_change_party()
