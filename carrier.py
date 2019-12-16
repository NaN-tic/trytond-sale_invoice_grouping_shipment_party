from trytond.model import fields
from trytond.pool import PoolMeta, Pool

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


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

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
