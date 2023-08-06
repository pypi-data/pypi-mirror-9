# -*- coding: utf-8 -*-
"""
    sale_channel.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction
from trytond.pyson import Eval
from trytond.model import ModelView, fields, ModelSQL

__metaclass__ = PoolMeta
__all__ = ['SaleChannel', 'ReadUser', 'WriteUser']

STATES = {
    'readonly': ~Eval('active', True),
}
DEPENDS = ['active']


class SaleChannel(ModelSQL, ModelView):
    """
    Sale Channel model
    """
    __name__ = 'sale.channel'

    name = fields.Char(
        'Name', required=True, select=True, states=STATES, depends=DEPENDS
    )
    code = fields.Char(
        'Code', select=True, states={'readonly': Eval('code', True)},
        depends=['code']
    )
    active = fields.Boolean('Active', select=True)
    company = fields.Many2One(
        'company.company', 'Company', required=True, select=True,
        states=STATES, depends=DEPENDS
    )
    address = fields.Many2One(
        'party.address', 'Address', domain=[
            ('party', '=', Eval('company_party')),
        ], depends=['company_party']
    )
    source = fields.Selection(
        'get_source', 'Source', required=True, states=STATES, depends=DEPENDS
    )

    read_users = fields.Many2Many(
        'sale.channel-read-res.user', 'channel', 'user', 'Read Users'
    )
    create_users = fields.Many2Many(
        'sale.channel-write-res.user', 'channel', 'user', 'Create Users'
    )

    warehouse = fields.Many2One(
        'stock.location', "Warehouse", required=True,
        domain=[('type', '=', 'warehouse')]
    )
    invoice_method = fields.Selection(
        [
            ('manual', 'Manual'),
            ('order', 'On Order Processed'),
            ('shipment', 'On Shipment Sent')
        ], 'Invoice Method', required=True
    )
    shipment_method = fields.Selection(
        [
            ('manual', 'Manual'),
            ('order', 'On Order Processed'),
            ('invoice', 'On Invoice Paid'),
        ], 'Shipment Method', required=True
    )
    currency = fields.Many2One(
        'currency.currency', 'Currency', required=True
    )
    price_list = fields.Many2One(
        'product.price_list', 'Price List', required=True
    )
    payment_term = fields.Many2One(
        'account.invoice.payment_term', 'Payment Term', required=True
    )
    company_party = fields.Function(
        fields.Many2One('party.party', 'Company Party'),
        'on_change_with_company_party'
    )

    @classmethod
    def get_source(cls):
        """
        Get the source
        """
        return [('manual', 'Manual')]

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_currency():
        pool = Pool()
        Company = pool.get('company.company')
        Channel = pool.get('sale.channel')

        company_id = Channel.default_company()
        company = Company(company_id)
        return company.currency.id

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @fields.depends('company')
    def on_change_with_company_party(self, name=None):
        Company = Pool().get('company.company')
        company = self.company
        if not company:
            company = Company(SaleChannel.default_company())  # pragma: nocover
        return company and company.party.id or None


class ReadUser(ModelSQL):
    """
    Read Users for Sale Channel
    """
    __name__ = 'sale.channel-read-res.user'

    channel = fields.Many2One(
        'sale.channel', 'Channel', ondelete='CASCADE', select=True,
        required=True
    )
    user = fields.Many2One(
        'res.user', 'User', ondelete='RESTRICT', required=True
    )


class WriteUser(ModelSQL):
    """
    Write Users for Sale Channel
    """
    __name__ = 'sale.channel-write-res.user'

    channel = fields.Many2One(
        'sale.channel', 'Channel', ondelete='CASCADE', select=True,
        required=True
    )
    user = fields.Many2One(
        'res.user', 'User', ondelete='RESTRICT', required=True
    )
