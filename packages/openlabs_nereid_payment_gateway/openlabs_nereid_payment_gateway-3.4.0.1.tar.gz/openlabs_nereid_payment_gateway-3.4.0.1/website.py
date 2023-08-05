"""
    website.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Bool, Eval

__metaclass__ = PoolMeta
__all__ = ['Website']


class Website:
    "Define the credit card handler"
    __name__ = 'nereid.website'

    accept_credit_card = fields.Boolean('Accept Credit Card')
    save_payment_profile = fields.Boolean(
        'Allow Saving Payment Profiles', states={
            'invisible': ~Bool(Eval('accept_credit_card'))
        }, depends=['accept_credit_card']
    )
    credit_card_gateway = fields.Many2One(
        'payment_gateway.gateway', 'Credit Card Gateway',
        states={
            'required': Bool(Eval('accept_credit_card')),
            'invisible': ~Bool(Eval('accept_credit_card'))
        }, depends=['accept_credit_card'],
        domain=[('method', '=', 'credit_card')]
    )
