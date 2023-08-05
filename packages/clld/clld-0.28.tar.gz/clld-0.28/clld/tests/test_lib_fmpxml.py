from __future__ import unicode_literals
import unittest
from io import open

from mock import Mock, patch

from clld.tests.util import TESTS_DIR


class Tests(unittest.TestCase):
    def test_Result(self):
        from clld.lib.fmpxml import Result

        Result(open(TESTS_DIR.joinpath('fmpxmlresult.xml'), encoding='utf8').read())

    def test_normalize_markup(self):
        from clld.lib.fmpxml import normalize_markup

        self.assertEqual('a\nb', normalize_markup('a<BR>b'))
        self.assertEqual(normalize_markup(''), None)
        self.assertEqual(normalize_markup('<SPAN STYLE="clear: right;">b</SPAN>'), 'b')
        assert normalize_markup('') is None
        assert normalize_markup('<span>bla</span>') == 'bla'
        s = '<span style="font-style: italic;">bla</span>'
        assert normalize_markup(s) == s
        s = '<span style="font-weight: bold;">bla</span>'
        assert normalize_markup(s) == s
        s = '<span style="font-variant: small-caps;">bla</span>'
        assert normalize_markup(s) == s

    def test_Client(self):
        from clld.lib.fmpxml import Client

        r = Mock(
            text=open(TESTS_DIR.joinpath('fmpxmlresult.xml'), encoding='utf8').read())

        with patch('clld.lib.fmpxml.requests', Mock(get=lambda *a, **kw: r)):
            c = Client(None, None, None, None, verbose=False)
            c.get('stuff')
            c.get('stuff')
