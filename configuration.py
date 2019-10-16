# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import fields, ModelSQL
from trytond.pool import Pool, PoolMeta
from trytond.modules.company.model import (
    CompanyMultiValueMixin, CompanyValueMixin)

__all__ = ['Configuration', 'ConfigurationCarrier']

sale_default_party_carrier = fields.Selection([
        (None, 'Party (default)'),
        ('shipment_party', 'Shipment Party'),
        ], 'Default Party Carrier')


class Configuration(metaclass=PoolMeta):
    __name__ = 'sale.configuration'
    sale_default_party_carrier = fields.MultiValue(sale_default_party_carrier)

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'sale_default_party_carrier':
            return pool.get('sale.configuration.sale_carrier')
        return super(Configuration, cls).multivalue_model(field)


class ConfigurationCarrier(metaclass=PoolMeta):
    __name__ = 'sale.configuration.sale_carrier'
    sale_default_party_carrier = sale_default_party_carrier
