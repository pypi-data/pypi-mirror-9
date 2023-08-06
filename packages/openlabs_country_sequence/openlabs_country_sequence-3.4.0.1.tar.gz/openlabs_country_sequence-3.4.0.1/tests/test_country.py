# -*- coding: utf-8 -*-
"""
    tests/test_country.py

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER
from trytond.transaction import Transaction
from trytond.tests.test_tryton import DB_NAME, CONTEXT


class TestCountry(unittest.TestCase):
    '''
    Test Country
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('country_sequence')

    def test0005create_country_with_sequence(self):
        '''
        Test if country is created with sequence
        '''
        Country = POOL.get('country.country')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            country, = Country.create([{
                'name': 'India',
                'code': 'IN'
            }])

            self.assertEqual(country.sequence, 300)

            country1, country2, country3 = Country.create([{
                'name': 'United States',
                'code': 'US',
                'sequence': 100
            }, {
                'name': 'Australia',
                'code': 'AU',
                'sequence': 400
            }, {
                'name': 'Canada',
                'code': 'CA',
                'sequence': 100
            }])

            self.assertEqual(country1.sequence, 100)

            countries = Country.search([])
            self.assertEqual(countries[0].code, 'CA')
            self.assertEqual(countries[1].code, 'US')


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestCountry)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
