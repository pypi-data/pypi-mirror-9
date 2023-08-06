# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from channel import SaleChannel, ReadUser, WriteUser
from product import ProductSaleChannelListing, Product
from sale import Sale
from user import User


def register():
    Pool.register(
        SaleChannel,
        ReadUser,
        WriteUser,
        User,
        Sale,
        ProductSaleChannelListing,
        Product,
        module='sale_channel', type_='model'
    )
