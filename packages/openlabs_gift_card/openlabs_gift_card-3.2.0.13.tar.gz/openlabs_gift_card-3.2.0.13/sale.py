# -*- coding: utf-8 -*-
"""
    sale.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import fields, ModelView
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval, Bool

__all__ = ['SaleLine', 'Sale']
__metaclass__ = PoolMeta


class SaleLine:
    "SaleLine"
    __name__ = 'sale.line'

    gift_card_delivery_mode = fields.Function(
        fields.Selection([
            ('virtual', 'Virtual'),
            ('physical', 'Physical'),
            ('combined', 'Combined'),
        ], 'Gift Card Delivery Mode', states={
            'invisible': ~Bool(Eval('is_gift_card')),
        }, depends=['is_gift_card']), 'on_change_with_gift_card_delivery_mode'
    )

    is_gift_card = fields.Function(
        fields.Boolean('Gift Card'),
        'on_change_with_is_gift_card'
    )
    gift_cards = fields.One2Many(
        'gift_card.gift_card', "sale_line", "Gift Cards", readonly=True
    )
    message = fields.Text(
        "Message", states={'invisible': ~Bool(Eval('is_gift_card'))}
    )

    recipient_email = fields.Char(
        "Recipient Email", states={
            'invisible': ~(
                Bool(Eval('is_gift_card')) &
                (Eval('gift_card_delivery_mode').in_(['virtual', 'combined']))
            ),
            'required': (
                Bool(Eval('is_gift_card')) &
                (Eval('gift_card_delivery_mode').in_(['virtual', 'combined']))
            ),
        }, depends=['gift_card_delivery_mode', 'is_gift_card']
    )

    recipient_name = fields.Char(
        "Recipient Name", states={
            'invisible': ~Bool(Eval('is_gift_card')),
        }, depends=['is_gift_card']
    )
    allow_open_amount = fields.Function(
        fields.Boolean("Allow Open Amount?", states={
            'invisible': ~Bool(Eval('is_gift_card'))
        }, depends=['is_gift_card']), 'on_change_with_allow_open_amount'
    )

    gc_price = fields.Many2One(
        'product.product.gift_card.price', "Gift Card Price", states={
            'required': (
                ~Bool(Eval('allow_open_amount')) & Bool(Eval('is_gift_card'))
            ),
            'invisible': ~(
                ~Bool(Eval('allow_open_amount')) & Bool(Eval('is_gift_card'))
            )
        }, depends=['allow_open_amount', 'is_gift_card', 'product'], domain=[
            ('product', '=', Eval('product'))
        ]
    )

    @fields.depends('product')
    def on_change_with_allow_open_amount(self, name=None):
        if self.product:
            return self.product.allow_open_amount

    @fields.depends('gc_price', 'unit_price')
    def on_change_gc_price(self, name=None):
        res = {}
        if self.gc_price:
            res['unit_price'] = self.gc_price.price
        return res

    @classmethod
    def __setup__(cls):
        super(SaleLine, cls).__setup__()

        cls.unit_price.states['readonly'] = (
            ~Bool(Eval('allow_open_amount')) & Bool(Eval('is_gift_card'))
        )

        cls._error_messages.update({
            'amounts_out_of_range':
                'Gift card amount must be within %s %s and %s %s'
        })

    @fields.depends('product', 'is_gift_card')
    def on_change_with_gift_card_delivery_mode(self, name=None):
        """
        Returns delivery mode of the gift card product
        """
        if not (self.product and self.is_gift_card):
            return None

        return self.product.gift_card_delivery_mode

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        default['gift_cards'] = None
        return super(SaleLine, cls).copy(lines, default=default)

    @fields.depends('product')
    def on_change_with_is_gift_card(self, name=None):
        """
        Returns boolean value to tell if product is gift card or not
        """
        return self.product and self.product.is_gift_card

    def get_invoice_line(self, invoice_type):
        """
        Pick up liability account from gift card configuration for invoices
        """
        GiftCardConfiguration = Pool().get('gift_card.configuration')

        lines = super(SaleLine, self).get_invoice_line(invoice_type)

        if lines and self.is_gift_card:
            liability_account = GiftCardConfiguration(1).liability_account

            if not liability_account:
                self.raise_user_error(
                    "Liability Account is missing from Gift Card "
                    "Configuration"
                )

            for invoice_line in lines:
                invoice_line.account = liability_account

        return lines

    @fields.depends('is_gift_card')
    def on_change_is_gift_card(self):
        ModelData = Pool().get('ir.model.data')

        if self.is_gift_card:
            return {
                'product': None,
                'description': 'Gift Card',
                'unit': ModelData.get_id('product', 'uom_unit'),
            }
        return {
            'description': None,
            'unit': None,
        }

    def create_gift_cards(self):
        '''
        Create the actual gift card for this line
        '''
        GiftCard = Pool().get('gift_card.gift_card')

        if not self.is_gift_card:
            # Not a gift card line
            return None

        if self.gift_cards:     # pragma: no cover
            # Cards already created
            return None

        product = self.product

        if product.allow_open_amount and not (
            product.gc_min <= self.unit_price <= product.gc_max
        ):
            self.raise_user_error(
                "amounts_out_of_range", (
                    self.sale.currency.code, product.gc_min,
                    self.sale.currency.code, product.gc_max
                )
            )

        gift_cards = GiftCard.create([{
            'amount': self.unit_price,
            'sale_line': self.id,
            'message': self.message,
            'recipient_email': self.recipient_email,
            'recipient_name': self.recipient_name,
            'origin': '%s,%d' % (self.sale.__name__, self.sale.id),
        } for each in range(0, int(self.quantity))])

        # TODO: have option of creating card after invoice is paid ?
        GiftCard.activate(gift_cards)

        return gift_cards


class Sale:
    "Sale"
    __name__ = 'sale.sale'

    def create_gift_cards(self):
        '''
        Create the gift cards if not already created
        '''
        for line in filter(lambda l: l.is_gift_card, self.lines):
            line.create_gift_cards()

    @classmethod
    @ModelView.button
    def process(cls, sales):
        """
        Create gift card on processing sale
        """

        super(Sale, cls).process(sales)

        for sale in sales:
            if sale.state not in ('confirmed', 'processing', 'done'):
                continue        # pragma: no cover
            sale.create_gift_cards()
