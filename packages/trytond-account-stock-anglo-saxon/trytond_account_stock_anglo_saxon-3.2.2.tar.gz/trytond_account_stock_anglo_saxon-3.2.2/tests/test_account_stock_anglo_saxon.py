#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends, doctest_dropdb


class AccountStockAngloSaxonTestCase(unittest.TestCase):
    'Test Account Stock Anglo Saxon module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_stock_anglo_saxon')

    def test0005views(self):
        'Test views'
        test_view('account_stock_anglo_saxon')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountStockAngloSaxonTestCase))
    suite.addTests(doctest.DocFileSuite(
            'scenario_account_stock_anglo_saxon.rst',
            setUp=doctest_dropdb, tearDown=doctest_dropdb, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    suite.addTests(doctest.DocFileSuite(
            'scenario_account_stock_anglo_saxon_with_drop_shipment.rst',
            setUp=doctest_dropdb, tearDown=doctest_dropdb, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
