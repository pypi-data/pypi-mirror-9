# -*- coding: utf-8 -*-
import unittest
import doctest
from pprint import pprint
from interlude import interact
import lxml.etree as etree


optionflags = \
    doctest.NORMALIZE_WHITESPACE | \
    doctest.ELLIPSIS | \
    doctest.REPORT_ONLY_FIRST_FAILURE


TESTFILES = [
    'tsf.rst',
    'utils.rst',
    'base.rst',
    'common.rst',
    'compound.rst',
    'controller.rst',
    'table.rst',
    'resources.rst',
]


def fxml(xml):
    et = etree.fromstring(xml)
    return etree.tostring(et, pretty_print=True)


def pxml(xml):
    print fxml(xml)


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            filename,
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint,
                   'pxml': pxml},
        ) for filename in TESTFILES
    ])


if __name__ == '__main__':                                 # pragma NO COVERAGE
    unittest.main(defaultTest='test_suite')                # pragma NO COVERAGE
