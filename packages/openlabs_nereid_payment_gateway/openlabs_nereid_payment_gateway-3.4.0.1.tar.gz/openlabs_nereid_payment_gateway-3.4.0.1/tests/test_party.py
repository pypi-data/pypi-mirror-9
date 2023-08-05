# -*- coding: utf-8 -*-
'''

    nereid_payment_gateway test suite

    :copyright: (c) 2010-2015 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details
'''
import unittest

import json
import pycountry
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from trytond.transaction import Transaction
from nereid.testing import NereidTestCase
from nereid import current_user


class TestCreditCard(NereidTestCase):
    "Test Payment profiles"

    def setUp(self):

        trytond.tests.test_tryton.install_module('nereid_payment_gateway')

        self.Language = POOL.get('ir.lang')
        self.NereidWebsite = POOL.get('nereid.website')
        self.Country = POOL.get('country.country')
        self.Subdivision = POOL.get('country.subdivision')
        self.Currency = POOL.get('currency.currency')
        self.NereidUser = POOL.get('nereid.user')
        self.User = POOL.get('res.user')
        self.Party = POOL.get('party.party')
        self.Company = POOL.get('company.company')
        self.Locale = POOL.get('nereid.website.locale')

        self.templates = {
            'my-cards.jinja':
                '{{ current_user.party.payment_profiles| length }}',
            'add-card.jinja':
            '''
            {% for error in form.address.errors %}
                {{ error }}
            {% endfor %}
            ''',
        }

    def _create_dummy_gateway_for_site(self):
        """
        A helper function that creates the authorize.net gateway and assigns
        it to the websites.
        """
        PaymentGateway = POOL.get('payment_gateway.gateway')
        Journal = POOL.get('account.journal')

        cash_journal, = Journal.search([
            ('name', '=', 'Cash')
        ])

        with Transaction().set_context(use_dummy=True):
            self.gateway = PaymentGateway(
                name='Dummy Gateway',
                journal=cash_journal,
                provider='dummy',
                method='credit_card',
            )
            self.gateway.save()

        websites = self.NereidWebsite.search([])
        self.NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': self.gateway.id,
        })

    def _create_countries(self, count=5):
        """
        Create some sample countries and subdivisions
        """
        for country in list(pycountry.countries)[0:count]:
            countries = self.Country.create([{
                'name': country.name,
                'code': country.alpha2,
            }])
            try:
                divisions = pycountry.subdivisions.get(
                    country_code=country.alpha2
                )
            except KeyError:
                pass
            else:
                for subdivision in list(divisions)[0:count]:
                    self.Subdivision.create([{
                        'country': countries[0].id,
                        'name': subdivision.name,
                        'code': subdivision.code,
                        'type': subdivision.type.lower(),
                    }])

    def login(self, client, username, password, assert_=True):
        """
        Tries to login.

        .. note::
            This method MUST be called within a context

        :param client: Instance of the test client
        :param username: The username, usually email
        :param password: The password to login
        :param assert_: Boolean value to indicate if the login has to be
                        ensured. If the login failed an assertion error would
                        be raised
        """
        rv = client.post(
            '/login', data={
                'email': username,
                'password': password,
            }
        )
        if assert_:
            self.assertEqual(rv.status_code, 302)
        return rv

    def setup_defaults(self):
        """
        Setting up default values.
        """

        usd, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])

        # Create parties
        self.party, = self.Party.create([{
            'name': 'openlabs',
        }])

        self.party2, = self.Party.create([{
            'name': 'Registered User',
        }])

        self.party3, = self.Party.create([{
            'name': 'Registered User 2',
        }])

        self.company, = self.Company.create([{
            'party': self.party,
            'currency': usd,
        }])

        # Create test users
        self.registered_user, = self.NereidUser.create([{
            'party': self.party2.id,
            'display_name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company.id,
        }])
        self.registered_user2, = self.NereidUser.create([{
            'party': self.party3.id,
            'display_name': 'Registered User 2',
            'email': 'email2@example.com',
            'password': 'password2',
            'company': self.company.id,
        }])

        # create countries
        self._create_countries()
        self.available_countries = self.Country.search([], limit=5)

        en_us, = self.Language.search([('code', '=', 'en_US')])

        self.locale_en_us, = self.Locale.create([{
            'code': 'en_US',
            'language': en_us.id,
            'currency': usd.id,
        }])

        self.NereidWebsite.create([{
            'name': 'localhost',
            'company': self.company.id,
            'application_user': USER,
            'default_locale': self.locale_en_us.id,
            'countries': [('add', self.available_countries)],
        }])

    def test_0010_add_payment_profile(self):
        """
        Test to add a new payment profile.
        """
        Address = POOL.get('party.address')

        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:

                self.login(c, 'email@example.com', 'password')

                address, = Address.create([{
                    'party': self.party2.id,
                    'name': 'Name',
                    'street': 'Street',
                    'streetbis': 'StreetBis',
                    'zip': 'zip',
                    'city': 'City',
                    'country': self.available_countries[0].id,
                    'subdivision':
                        self.available_countries[0].subdivisions[0].id,
                }])
                # Define a new payment gateway
                self._create_dummy_gateway_for_site()
                self.assertEqual(
                    len(current_user.party.payment_profiles), 0
                )

                with Transaction().set_context({'dummy_succeed': True}):
                    rv = c.post(
                        '/my-cards/add-card',
                        data={
                            'owner': 'Test User 1',
                            'number': '4111111111111111',
                            'expiry_month': '01',
                            'expiry_year': '2018',
                            'cvv': '123',
                            'address': address.id,
                        }
                    )
                    self.assertEqual(
                        len(current_user.party.payment_profiles), 1
                    )

                    # Test to handel xhr request
                    rv = c.post(
                        '/my-cards/add-card',
                        data={
                            'owner': 'Test User 2',
                            'number': '4111111111111111',
                            'expiry_month': '05',
                            'expiry_year': '2020',
                            'cvv': '111',
                            'address': address.id,
                        }, headers=[('X-Requested-With', 'XMLHttpRequest')]

                    )
                    self.assertEqual(
                        len(current_user.party.payment_profiles), 2
                    )
                    self.assertEqual(rv.status_code, 200)

    def test_0020_view_payment_profiles(self):
        """
        Test to view stored credit cards.
        """

        Address = POOL.get('party.address')
        Profile = POOL.get('party.payment_profile')
        Gateway = POOL.get('payment_gateway.gateway')
        Journal = POOL.get('account.journal')

        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                self.login(c, 'email@example.com', 'password')

                address, = Address.create([{
                    'party': self.party2.id,
                    'name': 'Name',
                    'street': 'Street',
                    'streetbis': 'StreetBis',
                    'zip': 'zip',
                    'city': 'City',
                    'country': self.available_countries[0].id,
                    'subdivision':
                        self.available_countries[0].subdivisions[0].id,
                }])

                self._create_dummy_gateway_for_site()
                self.assertEqual(
                    len(current_user.party.payment_profiles), 0
                )

                gateway, = Gateway.search(['name', '=', 'Dummy Gateway'])

                rv = c.get('/my-cards')
                self.assertEqual(rv.data, '0')

                cash_journal, = Journal.search([
                    ('name', '=', 'Cash')
                ])
                profile, = Profile.create([{
                    'last_4_digits': '1111',
                    'sequence': '10',
                    'expiry_month': '01',
                    'expiry_year': '2018',
                    'address': address.id,
                    'party': current_user.party.id,
                    'provider_reference': '27478839|25062702',
                    'gateway': gateway.id,
                }])

                with Transaction().set_context({'dummy_succeed': True}):

                    rv = c.get('/my-cards')
                    self.assertEqual(rv.data, '1')

                profile, = Profile.create([{
                    'last_4_digits': '1131',
                    'sequence': '10',
                    'expiry_month': '02',
                    'expiry_year': '2018',
                    'address': address.id,
                    'party': current_user.party.id,
                    'provider_reference': '27478839|25062710',
                    'gateway': gateway.id,
                }])

                with Transaction().set_context({'dummy_succeed': True}):
                    rv = c.get('/my-cards')
                    self.assertEqual(rv.data, '2')

                # Test to handel xhr request
                rv = c.get(
                    'my-cards',
                    headers=[('X-Requested-With', 'XMLHttpRequest')]
                )
                json_data = json.loads(rv.data)['payment_profile']

                self.assertEqual(len(json_data), 2)
                self.assertEqual(json_data[0]['last_4_digits'], '1111')
                self.assertEqual(json_data[1]['last_4_digits'], '1131')

    def test_0040_add_card_with_invalid_address(self):
        """
        Test for user trying to add card with invalid billing address.
        """
        Address = POOL.get('party.address')

        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:

                self.login(c, 'email@example.com', 'password')

                address, = Address.create([{
                    'party': self.party2.id,
                    'name': 'Name',
                    'street': 'Street',
                    'streetbis': 'StreetBis',
                    'zip': 'zip',
                    'city': 'City',
                    'country': self.available_countries[0].id,
                    'subdivision':
                        self.available_countries[0].subdivisions[0].id,
                }])
                # Define a new payment gateway
                self._create_dummy_gateway_for_site()

                with Transaction().set_context({'dummy_succeed': True}):

                    # request to add credit card with invalid card number
                    rv = c.post(
                        '/my-cards/add-card',
                        data={
                            'owner': 'Test User',
                            'number': '4111111111111111',
                            'expiry_month': '01',
                            'expiry_year': '2018',
                            'cvv': '111',
                            'address': 123,
                        }
                    )
                self.assertTrue(
                    'Address you selected is not valid.'
                    in rv.data
                )

    def test_0050_remove_payment_profile(self):
        """
        Test to inactivate payment profile when user want to remove it.
        """
        Address = POOL.get('party.address')
        Profile = POOL.get('party.payment_profile')
        Gateway = POOL.get('payment_gateway.gateway')
        Journal = POOL.get('account.journal')

        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                self.login(c, 'email@example.com', 'password')

                address, = Address.create([{
                    'party': self.party2.id,
                    'name': 'Name',
                    'street': 'Street',
                    'streetbis': 'StreetBis',
                    'zip': 'zip',
                    'city': 'City',
                    'country': self.available_countries[0].id,
                    'subdivision':
                        self.available_countries[0].subdivisions[0].id,
                }])

                self._create_dummy_gateway_for_site()
                cash_journal, = Journal.search([
                    ('name', '=', 'Cash')
                ])
                gateway, = Gateway.search(['name', '=', 'Dummy Gateway'])

                self.assertEqual(
                    len(current_user.party.payment_profiles), 0
                )
                profile1, = Profile.create([{
                    'last_4_digits': '1111',
                    'sequence': '10',
                    'expiry_month': '01',
                    'expiry_year': '2018',
                    'address': address.id,
                    'party': current_user.party.id,
                    'provider_reference': '27478839|25062702',
                    'gateway': gateway.id,
                }])

                profile2, = Profile.create([{
                    'last_4_digits': '1131',
                    'sequence': '10',
                    'expiry_month': '02',
                    'expiry_year': '2018',
                    'address': address.id,
                    'party': current_user.party.id,
                    'provider_reference': '27478839|25062710',
                    'gateway': gateway.id,
                }])

                self.assertEqual(
                    len(current_user.party.payment_profiles), 2
                )

                with Transaction().set_context({'dummy_succeed': True}):

                    rv = c.post(
                        '/my-cards/remove-card',
                        data={
                            'profile_id':
                            current_user.party.payment_profiles[0].id,
                        }
                    )

                    self.assertEqual(rv.status_code, 302)
                    self.assertEqual(
                        len(current_user.party.payment_profiles), 1
                    )
                    # Remove payment profile by xhr request
                    rv = c.post(
                        '/my-cards/remove-card',
                        data={
                            'profile_id':
                            current_user.party.payment_profiles[0].id,
                        }, headers=[('X-Requested-With', 'XMLHttpRequest')]
                    )
                    self.assertEqual(rv.status_code, 200)
                    self.assertEqual(
                        len(current_user.party.payment_profiles), 0
                    )

    def test_0060_remove_invalid_payment_profile(self):
        """
        Test to check if payment profile user wants to remove is valid.
        """
        Address = POOL.get('party.address')
        Profile = POOL.get('party.payment_profile')
        Gateway = POOL.get('payment_gateway.gateway')
        Journal = POOL.get('account.journal')

        with Transaction().start(DB_NAME, USER, CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                self.login(c, 'email@example.com', 'password')

                address, = Address.create([{
                    'party': self.party2.id,
                    'name': 'Name',
                    'street': 'Street',
                    'streetbis': 'StreetBis',
                    'zip': 'zip',
                    'city': 'City',
                    'country': self.available_countries[0].id,
                    'subdivision':
                        self.available_countries[0].subdivisions[0].id,
                }])

                self._create_dummy_gateway_for_site()
                cash_journal, = Journal.search([
                    ('name', '=', 'Cash')
                ])
                gateway, = Gateway.search(['name', '=', 'Dummy Gateway'])

                self.assertEqual(
                    len(current_user.party.payment_profiles), 0
                )
                profile1, = Profile.create([{
                    'last_4_digits': '1111',
                    'sequence': '10',
                    'expiry_month': '01',
                    'expiry_year': '2018',
                    'address': address.id,
                    'party': current_user.party.id,
                    'provider_reference': '27478839|25062702',
                    'gateway': gateway.id,
                }])

                self.assertEqual(
                    len(current_user.party.payment_profiles), 1
                )

                with Transaction().set_context({'dummy_succeed': True}):

                    rv = c.post(
                        '/my-cards/remove-card',
                        data={
                            'profile_id': 123,
                        }
                    )
                    self.assertEqual(rv.status_code, 403)
                    self.assertEqual(
                        len(current_user.party.payment_profiles), 1
                    )


def suite():
    "Nereid test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestCreditCard)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
