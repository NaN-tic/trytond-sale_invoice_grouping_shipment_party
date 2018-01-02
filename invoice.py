# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['Invoice']


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'
    shipment_party = fields.Many2One('party.party', 'Shipment Party',
        states={
            'readonly': (Eval('state') != 'draft'),
            'invisible': (Eval('type') in ('in_invoice', 'in_credit_note')),
            },
        depends=['state'])

    @classmethod
    def __setup__(cls):
        super(Invoice,cls).__setup__()
        cls._error_messages.update({
                'error_party_payer': ('Party "%s" cannot be used as a payer'
                    ' because it has a payer defined'),
                })

    @classmethod
    def validate(cls, invoices):
        super(Invoice, cls).validate(invoices)
        for invoice in invoices:
            invoice.check_shipment_party()

    def check_shipment_party(self):
        if (self.state == 'draft'
                and self.type in ('out_invoice', 'out_credit_note')
                and self.party.party_sale_payer):
            self.raise_user_error('error_party_payer', self.party.rec_name)

    @fields.depends('shipment_party', methods=['party'])
    def on_change_shipment_party(self):
         if self.shipment_party:
            if self.shipment_party.party_sale_payer:
                self.party = self.shipment_party.party_sale_payer
            else:
                self.party = self.shipment_party
            self.on_change_party()

            if hasattr(self, 'invoice_discount'):
                self.invoice_discount = self.on_change_with_invoice_discount()
