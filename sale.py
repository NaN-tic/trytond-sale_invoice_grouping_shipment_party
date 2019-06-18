# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Sale']


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    @classmethod
    def validate(cls, sales):
        super(Sale, cls).validate(sales)
        for sale in sales:
            sale.check_shipment_party()

    def check_shipment_party(self):
        if self.party.party_sale_payer:
            raise UserError(
                gettext('sale_invoice_grouping_shipment_party.msg_error_party_payer',
                name=self.party.rec_name,
                ))

    @property
    def _invoice_grouping_fields(self):
        return super(Sale, self)._invoice_grouping_fields + ('shipment_party',)

    def _get_grouped_invoice_domain(self, invoice):
        invoice_domain = super(Sale, self)._get_grouped_invoice_domain(invoice)
        if self.shipment_party:
            if ('shipment_party', '=', None) in invoice_domain:
                invoice_domain[
                    invoice_domain.index(('shipment_party', '=', None))
                    ] = ('shipment_party', '=', self.shipment_party)
            else:
                invoice_domain.append(
                    ('shipment_party', '=', self.shipment_party))
        return invoice_domain

    def _get_invoice_sale(self):
        invoice = super(Sale, self)._get_invoice_sale()
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


    @fields.depends('carrier')
    def on_change_party(self):
        super(Sale, self).on_change_party()
        Config = Pool().get('sale.configuration')
        config = Config(1)
        if config:
            config = config.sale_default_party_carrier
        if config == 'shipment_party' and self.shipment_party:
            if self.shipment_party.carrier:
                self.carrier = self.shipment_party.carrier
