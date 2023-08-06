# -*- coding: utf-8 -*-
"""
    stock.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from decimal import Decimal, ROUND_UP
import base64
from lxml import etree

from ups.shipping_package import ShipmentConfirm, ShipmentAccept
from ups.base import PyUPSException
from trytond.model import fields, ModelView
from trytond.wizard import Wizard, StateView, Button
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.rpc import RPC

from .sale import UPS_PACKAGE_TYPES

__metaclass__ = PoolMeta
__all__ = [
    'ShipmentOut', 'StockMove', 'ShippingUps',
    'GenerateShippingLabel'
]

STATES = {
    'readonly': Eval('state') == 'done',
}


class ShipmentOut:
    "Shipment Out"
    __name__ = 'stock.shipment.out'

    is_ups_shipping = fields.Function(
        fields.Boolean('Is Shipping', readonly=True),
        'get_is_ups_shipping'
    )
    ups_service_type = fields.Many2One(
        'ups.service', 'UPS Service Type', states=STATES, depends=['state']
    )
    ups_package_type = fields.Selection(
        UPS_PACKAGE_TYPES, 'Package Content Type', states=STATES,
        depends=['state']
    )
    ups_saturday_delivery = fields.Boolean(
        "Is Saturday Delivery", states=STATES, depends=['state']
    )

    def _get_weight_uom(self):
        """
        Returns uom for ups
        """
        UPSConfiguration = Pool().get('ups.configuration')

        weight_uom = UPSConfiguration(1).weight_uom

        if self.is_ups_shipping and weight_uom:
            return weight_uom

        return super(ShipmentOut, self)._get_weight_uom()

    @staticmethod
    def default_ups_package_type():
        Config = Pool().get('sale.configuration')
        config = Config(1)
        return config.ups_package_type

    @staticmethod
    def default_ups_service_type():
        Config = Pool().get('sale.configuration')
        config = Config(1)
        return config.ups_service_type and config.ups_service_type.id or None

    @staticmethod
    def default_ups_saturday_delivery():
        return False

    def get_is_ups_shipping(self, name):
        """
        Check if shipping is from UPS
        """
        return self.carrier and self.carrier.carrier_cost_method == 'ups'

    @classmethod
    def __setup__(cls):
        super(ShipmentOut, cls).__setup__()
        # There can be cases when people might want to use a different
        # shipment carrier at any state except `done`.
        cls.carrier.states = STATES
        cls._error_messages.update({
            'ups_wrong_carrier':
                'Carrier for selected shipment is not UPS',
            'ups_service_type_missing':
                'UPS service type missing.',
            'tracking_number_already_present':
                'Tracking Number is already present for this shipment.',
            'invalid_state': 'Labels can only be generated when the '
                'shipment is in Packed or Done states only',
        })
        cls.__rpc__.update({
            'make_ups_labels': RPC(readonly=False, instantiate=0),
            'get_ups_shipping_cost': RPC(readonly=False, instantiate=0),
        })

    def _get_ups_packages(self):
        """
        Return UPS Packages XML
        """
        UPSConfiguration = Pool().get('ups.configuration')

        ups_config = UPSConfiguration(1)
        package_type = ShipmentConfirm.packaging_type(
            Code=self.ups_package_type
        )  # FIXME: Support multiple packaging type

        weight = self.package_weight.quantize(
            Decimal('.01'), rounding=ROUND_UP
        )
        package_weight = ShipmentConfirm.package_weight_type(
            Weight=str(weight),
            Code=ups_config.weight_uom_code,
        )
        package_service_options = ShipmentConfirm.package_service_options_type(
            ShipmentConfirm.insured_value_type(MonetaryValue='0')
        )
        package_container = ShipmentConfirm.package_type(
            package_type,
            package_weight,
            package_service_options
        )
        return [package_container]

    def _get_carrier_context(self):
        "Pass shipment in the context"
        context = super(ShipmentOut, self)._get_carrier_context()

        if not self.carrier.carrier_cost_method == 'ups':
            return context

        context = context.copy()
        context['shipment'] = self.id
        return context

    def _get_shipment_confirm_xml(self):
        """
        Return XML of shipment for shipment_confirm
        """
        Company = Pool().get('company.company')
        UPSConfiguration = Pool().get('ups.configuration')

        ups_config = UPSConfiguration(1)
        if not self.ups_service_type:
            self.raise_user_error('ups_service_type_missing')

        payment_info_prepaid = \
            ShipmentConfirm.payment_information_prepaid_type(
                AccountNumber=ups_config.shipper_no
            )
        payment_info = ShipmentConfirm.payment_information_type(
            payment_info_prepaid)
        packages = self._get_ups_packages()
        shipment_service = ShipmentConfirm.shipment_service_option_type(
            SaturdayDelivery='1' if self.ups_saturday_delivery
            else 'None'
        )
        description = ','.join([
            move.product.name for move in self.outgoing_moves
        ])

        shipment_args = [
            self.warehouse.address.to_ups_shipper(),
            self.delivery_address.to_ups_to_address(),
            self.warehouse.address.to_ups_from_address(),
            ShipmentConfirm.service_type(Code=self.ups_service_type.code),
            payment_info, shipment_service,
        ]
        if ups_config.negotiated_rates:
            shipment_args.append(
                ShipmentConfirm.rate_information_type(negotiated=True)
            )
        if self.warehouse.address.country.code == 'US' and \
                self.delivery_address.country.code in ['PR', 'CA']:
            # Special case for US to PR or CA InvoiceLineTotal should be sent
            monetary_value = str(sum(map(
                lambda move: move.get_monetary_value_for_ups(),
                self.outgoing_moves
            )))

            company_id = Transaction().context.get('company')
            if not company_id:
                self.raise_user_error("Company is not in context")

            company = Company(company_id)
            shipment_args.append(ShipmentConfirm.invoice_line_total_type(
                MonetaryValue=monetary_value,
                CurrencyCode=company.currency.code
            ))

        shipment_args.extend(packages)
        shipment_confirm = ShipmentConfirm.shipment_confirm_request_type(
            *shipment_args, Description=description[:35]
        )
        return shipment_confirm

    @classmethod
    def _get_ups_shipment_cost(cls, shipment_confirm):
        """
        The shipment_confirm is an xml container in the response which has the
        standard rates and negotiated rates. This method should extract the
        value and return it with the currency
        """
        Currency = Pool().get('currency.currency')
        UPSConfiguration = Pool().get('ups.configuration')

        ups_config = UPSConfiguration(1)
        shipment_charges = shipment_confirm.ShipmentCharges

        currency, = Currency.search([
            ('code', '=', str(
                shipment_charges.TotalCharges.CurrencyCode
            ))
        ])

        if ups_config.negotiated_rates and \
                hasattr(shipment_confirm, 'NegotiatedRates'):
            # If there are negotiated rates return that instead
            charges = shipment_confirm.NegotiatedRates.NetSummaryCharges
            charges = currency.round(Decimal(
                str(charges.GrandTotal.MonetaryValue)
            ))
        else:
            charges = currency.round(
                Decimal(str(shipment_charges.TotalCharges.MonetaryValue))
            )
        return charges, currency

    def get_ups_shipping_cost(self):
        """Returns the calculated shipping cost as sent by ups

        :returns: The shipping cost with currency
        """
        UPSConfiguration = Pool().get('ups.configuration')
        Carrier = Pool().get('carrier')

        ups_config = UPSConfiguration(1)
        carrier, = Carrier.search(['carrier_cost_method', '=', 'ups'])

        shipment_confirm = self._get_shipment_confirm_xml()
        shipment_confirm_instance = ups_config.api_instance(call="confirm")

        # Logging.
        ups_config.logger.debug(
            'Making Shipment Confirm Request for'
            'Shipment ID: {0} and Carrier ID: {1}'
            .format(self.id, carrier.id)
        )
        ups_config.logger.debug(
            '--------SHIPMENT CONFIRM REQUEST--------\n%s'
            '\n--------END REQUEST--------'
            % etree.tostring(shipment_confirm, pretty_print=True)
        )

        try:
            response = shipment_confirm_instance.request(shipment_confirm)

            # Logging.
            ups_config.logger.debug(
                '--------SHIPMENT CONFIRM RESPONSE--------\n%s'
                '\n--------END RESPONSE--------'
                % etree.tostring(response, pretty_print=True)
            )
        except PyUPSException, e:
            self.raise_user_error(unicode(e[0]))

        shipping_cost, currency = self._get_ups_shipment_cost(response)

        return shipping_cost, currency.id

    def make_ups_labels(self):
        """
        Make labels for the given shipment

        :return: Tracking number as string
        """
        Attachment = Pool().get('ir.attachment')
        UPSConfiguration = Pool().get('ups.configuration')
        Currency = Pool().get('currency.currency')

        ups_config = UPSConfiguration(1)
        if self.state not in ('packed', 'done'):
            self.raise_user_error('invalid_state')

        if not self.is_ups_shipping:
            self.raise_user_error('ups_wrong_carrier')

        if self.tracking_number:
            self.raise_user_error('tracking_number_already_present')

        shipment_confirm = self._get_shipment_confirm_xml()
        shipment_confirm_instance = ups_config.api_instance(call="confirm")

        # Logging.
        ups_config.logger.debug(
            'Making Shipment Confirm Request for'
            'Shipment ID: {0} and Carrier ID: {1}'
            .format(self.id, self.carrier.id)
        )
        ups_config.logger.debug(
            '--------SHIPMENT CONFIRM REQUEST--------\n%s'
            '\n--------END REQUEST--------'
            % etree.tostring(shipment_confirm, pretty_print=True)
        )

        try:
            response = shipment_confirm_instance.request(shipment_confirm)

            # Logging.
            ups_config.logger.debug(
                '--------SHIPMENT CONFIRM RESPONSE--------\n%s'
                '\n--------END RESPONSE--------'
                % etree.tostring(response, pretty_print=True)
            )
        except PyUPSException, e:
            self.raise_user_error(unicode(e[0]))

        digest = ShipmentConfirm.extract_digest(response)

        shipment_accept = ShipmentAccept.shipment_accept_request_type(digest)

        shipment_accept_instance = ups_config.api_instance(call="accept")

        # Logging.
        ups_config.logger.debug(
            'Making Shipment Accept Request for'
            'Shipment ID: {0} and Carrier ID: {1}'
            .format(self.id, self.carrier.id)
        )
        ups_config.logger.debug(
            '--------SHIPMENT ACCEPT REQUEST--------\n%s'
            '\n--------END REQUEST--------'
            % etree.tostring(shipment_accept, pretty_print=True)
        )

        try:
            response = shipment_accept_instance.request(shipment_accept)

            # Logging.
            ups_config.logger.debug(
                '--------SHIPMENT ACCEPT RESPONSE--------\n%s'
                '\n--------END RESPONSE--------'
                % etree.tostring(response, pretty_print=True)
            )
        except PyUPSException, e:
            self.raise_user_error(unicode(e[0]))

        if len(response.ShipmentResults.PackageResults) > 1:
            self.raise_user_error('ups_multiple_packages_not_supported')

        shipment_res = response.ShipmentResults
        package, = shipment_res.PackageResults
        tracking_number = package.TrackingNumber.pyval

        currency, = Currency.search([
            ('code', '=', str(
                shipment_res.ShipmentCharges.TotalCharges.CurrencyCode
            ))
        ])
        shipping_cost = currency.round(Decimal(
            str(shipment_res.ShipmentCharges.TotalCharges.MonetaryValue)
        ))
        self.__class__.write([self], {
            'tracking_number': unicode(tracking_number),
            'cost': shipping_cost,
            'cost_currency': currency,
        })

        Attachment.create([{
            'name': "%s_%s_.png" % (
                tracking_number,
                shipment_res.ShipmentIdentificationNumber.pyval
            ),
            'data': buffer(base64.decodestring(
                package.LabelImage.GraphicImage.pyval
            )),
            'resource': '%s,%s' % (self.__name__, self.id)
        }])
        return tracking_number

    @fields.depends('ups_service_type')
    def on_change_carrier(self):
        """
        Show/Hide UPS Tab in view on change of carrier
        """
        res = super(ShipmentOut, self).on_change_carrier()

        res['is_ups_shipping'] = self.carrier and \
            self.carrier.carrier_cost_method == 'ups'

        return res


class StockMove:
    "Stock move"
    __name__ = "stock.move"

    def get_monetary_value_for_ups(self):
        """
        Returns monetary_value as required for ups
        """
        ProductUom = Pool().get('product.uom')

        # Find the quantity in the default uom of the product as the weight
        # is for per unit in that uom
        if self.uom != self.product.default_uom:
            quantity = ProductUom.compute_qty(
                self.uom,
                self.quantity,
                self.product.default_uom
            )
        else:
            quantity = self.quantity

        return Decimal(self.product.list_price) * Decimal(quantity)


class ShippingUps(ModelView):
    'Generate Labels'
    __name__ = 'shipping.label.ups'

    ups_service_type = fields.Many2One('ups.service', 'UPS Service Type')
    ups_package_type = fields.Selection(
        UPS_PACKAGE_TYPES, 'Package Content Type'
    )
    ups_saturday_delivery = fields.Boolean("Is Saturday Delivery ?")


class GenerateShippingLabel(Wizard):
    'Generate Labels'
    __name__ = 'shipping.label'

    ups_config = StateView(
        'shipping.label.ups',
        'shipping_ups.shipping_ups_configuration_view_form',
        [
            Button('Back', 'start', 'tryton-go-previous'),
            Button('Continue', 'generate', 'tryton-go-next'),
        ]
    )

    def default_ups_config(self, data):
        Config = Pool().get('sale.configuration')
        config = Config(1)
        shipment = self.start.shipment

        return {
            'ups_service_type': (
                shipment.ups_service_type and shipment.ups_service_type.id
            ) or (
                config.ups_service_type and config.ups_service_type.id
            ) or None,
            'ups_package_type': (
                shipment.ups_package_type or config.ups_package_type
            ),
            'ups_saturday_delivery': shipment.ups_saturday_delivery
        }

    def transition_next(self):
        state = super(GenerateShippingLabel, self).transition_next()

        if self.start.carrier.carrier_cost_method == 'ups':
            return 'ups_config'
        return state

    def update_shipment(self):
        shipment = super(GenerateShippingLabel, self).update_shipment()

        if self.start.carrier.carrier_cost_method == 'ups':
            shipment.ups_service_type = self.ups_config.ups_service_type
            shipment.ups_package_type = self.ups_config.ups_package_type
            shipment.ups_saturday_delivery = \
                self.ups_config.ups_saturday_delivery

        return shipment
