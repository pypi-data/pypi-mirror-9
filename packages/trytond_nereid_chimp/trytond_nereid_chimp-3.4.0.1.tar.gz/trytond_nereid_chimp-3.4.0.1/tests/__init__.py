# -*- coding: utf-8 -*-
'''

    Test Nereid Integration with MailChimp

    :copyright: (c) 2011-2012 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details

'''
import unittest

import trytond.tests.test_tryton

from .test_chimp import TestChimp


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests([
        unittest.TestLoader().loadTestsFromTestCase(TestChimp),
    ])
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
