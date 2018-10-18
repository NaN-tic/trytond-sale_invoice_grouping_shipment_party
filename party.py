# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.model import fields

__all__ = ['Party']


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    party_sale_payer = fields.Many2One('party.party', 'Party Sale Payer',
        help='Default party payer when selecting a shipment party on sales'
            ' or invoices.')
