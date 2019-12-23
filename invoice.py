# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Invoice']


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'
    shipment_party = fields.Many2One('party.party', 'Shipment Party',
        states={
            'readonly': (Eval('state') != 'draft'),
            'invisible': (Eval('type') == 'in'),
            },
        depends=['state'])

    @classmethod
    def validate(cls, invoices):
        super(Invoice, cls).validate(invoices)
        for invoice in invoices:
            invoice.check_shipment_party()

    def check_shipment_party(self):
        if (self.state == 'draft' and self.type == 'out'
                and self.party.party_sale_payer):
            raise UserError(gettext('sale_invoice_grouping_shipment_party.'
                    'msg_error_party_payer', name=self.party.rec_name,))

    @fields.depends('shipment_party', methods=['on_change_party'])
    def on_change_shipment_party(self):
        if self.shipment_party:
            if self.shipment_party.party_sale_payer:
                self.party = self.shipment_party.party_sale_payer
            else:
                self.party = self.shipment_party
            self.on_change_party()

            if hasattr(self, 'invoice_discount'):
                self.invoice_discount = self.on_change_with_invoice_discount()

        if hasattr(self, 'shipment_address'):
            delivery_address = None
            if self.party and not self.shipment_party:
                delivery_address = self.party.address_get(type='delivery')
            if self.shipment_party:
                delivery_address = self.shipment_party.address_get(
                    type='delivery')
            self.shipment_address = delivery_address

    def _credit(self):
        credit = super()._credit()
        credit.shipment_party = self.shipment_party
        return credit
