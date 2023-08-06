# -*- coding: utf-8 -*-
"""
    carrier

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from decimal import Decimal

from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction

__all__ = ['Carrier', 'UPSService', 'CarrierConfig']
__metaclass__ = PoolMeta


class CarrierConfig:
    "Carrier Configuration"
    __name__ = 'carrier.configuration'

    @classmethod
    def get_default_validation_providers(cls):
        """
        Add ups to validation provider list
        """
        methods = super(CarrierConfig, cls).get_default_validation_providers()
        methods.append(('ups', 'UPS'))
        return methods


class Carrier:
    "Carrier"
    __name__ = 'carrier'

    @classmethod
    def __setup__(cls):
        super(Carrier, cls).__setup__()
        selection = ('ups', 'UPS')
        if selection not in cls.carrier_cost_method.selection:
            cls.carrier_cost_method.selection.append(selection)

    def get_rates(self):
        """
        Return list of tuples as:
            [
                (<display method name>, <rate>, <currency>, <metadata>)
                ...
            ]
        """
        Sale = Pool().get('sale.sale')

        sale = Transaction().context.get('sale')

        if sale and self.carrier_cost_method == 'ups':
            return Sale(sale).get_ups_shipping_rates()

        return super(Carrier, self).get_rates()

    def _get_ups_service_name(self, service):
        """
        Return display name for ups service

        This method can be overridden by downstream module to change the default
        display name of service
        """
        return "%s %s" % (
            self.carrier_product.code, service.display_name or service.name
        )

    def get_sale_price(self):
        """Estimates the shipment rate for the current shipment

        The get_sale_price implementation by tryton's carrier module
        returns a tuple of (value, currency_id)

        :returns: A tuple of (value, currency_id which in this case is USD)
        """
        Sale = Pool().get('sale.sale')
        Shipment = Pool().get('stock.shipment.out')
        Currency = Pool().get('currency.currency')

        shipment_id = Transaction().context.get('shipment')
        sale_id = Transaction().context.get('sale')
        default_currency, = Currency.search([('code', '=', 'USD')])

        if Transaction().context.get('ignore_carrier_computation'):
            return Decimal('0'), default_currency.id
        if not (sale_id or shipment_id):
            return Decimal('0'), default_currency.id

        if self.carrier_cost_method != 'ups':
            return super(Carrier, self).get_sale_price()

        if sale_id:
            return Sale(sale_id).get_ups_shipping_cost()

        if shipment_id and shipment_id > 0:
            # get_ups_shipping_cost must not be called if shipment is not saved.
            # If shipment is saved/active record is created properly,
            # then the ID must be a positive integer.
            return Shipment(shipment_id).get_ups_shipping_cost()

        return Decimal('0'), default_currency.id


class UPSService(ModelSQL, ModelView):
    "UPS Service"
    __name__ = 'ups.service'

    active = fields.Boolean('Active', select=True)
    name = fields.Char('Name', required=True, select=True, readonly=True)
    code = fields.Char(
        'Service Code', required=True, select=True, readonly=True
    )
    display_name = fields.Char('Display Name', select=True)

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def check_xml_record(records, values):
        for key in values:
            if key not in ['display_name', 'active']:
                return False
        return True
