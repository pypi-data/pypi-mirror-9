# -*- coding: utf-8 -*-
"""
    nereid_mailchimp.test

    Test the mailchimp plugin for nereid

    :copyright: (c) 2010-2012 by Openlabs Technologies & Consulting (P) LTD.
    :license: GPLv3, see LICENSE for more details.
"""
import os
import sys
import json
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import (
    POOL, USER, DB_NAME, CONTEXT, test_view, test_depends
)
from nereid.testing import NereidTestCase
from trytond.transaction import Transaction


class TestChimp(NereidTestCase):
    "Chimp Test Case"

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test execution.
        """
        trytond.tests.test_tryton.install_module('nereid_chimp')

        self.Currency = POOL.get('currency.currency')
        self.Site = POOL.get('nereid.website')
        self.Company = POOL.get('company.company')
        self.NereidUser = POOL.get('nereid.user')
        self.Language = POOL.get('ir.lang')
        self.NereidWebsite = POOL.get('nereid.website')
        self.Party = POOL.get('party.party')
        self.Locale = POOL.get('nereid.website.locale')
        self.xhr_header = [
            ('X-Requested-With', 'XMLHttpRequest'),
        ]

    def setup_defaults(self):
        """
        Setup the defaults
        """
        usd, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])
        party1, = self.Party.create([{
            'name': 'Openlabs',
        }])
        company, = self.Company.create([{
            'party': party1.id,
            'currency': usd.id
        }])
        party2, = self.Party.create([{
            'name': 'Guest User',
        }])
        party3, = self.Party.create([{
            'name': 'Registered User',
        }])
        self.registered_user, = self.NereidUser.create([{
            'party': party3.id,
            'display_name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': company.id,
        }])

        # Create website
        en_us, = self.Language.search([('code', '=', 'en_US')])

        self.locale_en_us, = self.Locale.create([{
            'code': 'en_US',
            'language': en_us.id,
            'currency': usd.id,
        }])
        self.NereidWebsite.create([{
            'name': 'localhost',
            'company': company.id,
            'application_user': USER,
            'default_locale': self.locale_en_us.id,
            'currencies': [('add', [usd.id])],
            'mailchimp_api_key': '075986b700e22d414a34c34243d54658-us9',
            'mailchimp_default_list': 'LN TEST',
        }])

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('nereid_chimp')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()

    def test0010_list_subscription(self):
        '''
        Test if product has all the attributes of variation_attributes.
        '''
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            app = self.get_app()

            with app.test_client() as c:
                response = c.get('/mailing-list/subscribe')
                self.assertEqual(response.status_code, 405)

                response = c.post('/mailing-list/subscribe', data={
                    'email': 'tb@openlabs.co.in'
                }, headers=self.xhr_header)
                self.assertEqual(response.status_code, 409)
                rv_json = json.loads(response.data)
                self.assertTrue('already subscribed' in rv_json['message'])

                response = c.post('/mailing-list/subscribe', data={
                    'email': 'tb_do_not_exist@openlabs.co.in'
                }, headers=self.xhr_header)
                self.assertEqual(response.status_code, 200)
                rv_json = json.loads(response.data)
                self.assertTrue('successfully subscribed' in rv_json['message'])


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestChimp)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
