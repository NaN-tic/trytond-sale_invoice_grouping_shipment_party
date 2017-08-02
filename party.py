from trytond.pool import PoolMeta, Pool
from trytond.model import fields

__all__ = ['Party']


class Party:
    __name__ = 'party.party'
    __metaclass__ = PoolMeta
    party_sale_payer = fields.Many2One('party.party', 'Party Sale Payer',
        help='Default party payer when selecting a shipment party on sales'
            ' or invoices.')
