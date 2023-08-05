from __future__ import print_function, unicode_literals

import logging
import pickle
import unittest
from collections import OrderedDict

from rply import Token

from lua_table import lexer, parser, parse


INSTR = """
return {
\t["password"] = "secret";
}
"""


class TestLuaTebleLexer(unittest.TestCase):
    def test_lex_simple(self):
        tokens = list(lexer.lex(INSTR))
        self.assertEqual(tokens, [Token(u'RETURN', u'return'),
                                  Token(u'OPBRACE', u'{'),
                                  Token(u'OPBRAK', u'['),
                                  Token(u'STRING', u'"password"'),
                                  Token(u'CLBRAK', u']'),
                                  Token(u'STRING', u'"secret"'),
                                  Token(u'RECSEP', u';'),
                                  Token(u'CLBRACE', u'}')])

    def test_lex_roster(self):
        with open('test/data/roster.dat') as inf, \
                open('test/data/roster-lex.pkl', 'rb') as expf:
            tokens = list(lexer.lex(inf.read()))
            expected = pickle.load(expf)
        self.assertEqual(tokens, expected)


class TestLuaTebleParser(unittest.TestCase):
    def test_parse_account(self):
        logging.debug('\n%s', '=' * 60)
        with open('test/data/account.dat') as inf:
            instr = inf.read()
            #logging.debug('instr:\n%s', instr)
            pars = parser.parse(lexer.lex(instr))
            #logging.debug('pars = %s', pars)
            self.assertEqual(pars, OrderedDict([(u'password', u'secret')]))

    def test_parse_bigger_record(self):
        logging.debug('\n%s', '=' * 60)
        with open('test/data/multi-value.dat') as inf:
            pars = parser.parse(lexer.lex(inf.read()))
            expected = OrderedDict(
                [(u'lady01@bastards.com',
                  OrderedDict([(u'subscription', u'both'),
                               (u'groups', OrderedDict([(u'Church', True)])),
                               (u'name', u"Joan d'Arc")]))])
            logging.debug('pars = %s', pars)
            self.assertEqual(pars, expected)

    def test_parse_roster(self):
        logging.debug('\n%s', '=' * 60)
        with open('test/data/roster.dat') as inf, \
                open('test/data/roster-parse.pkl', 'rb') as expf:
            expected = pickle.load(expf)
            tokens = lexer.lex(inf.read())
            pars = parser.parse(tokens)
            self.assertEqual(pars, expected)

    def test_parse_method(self):
        logging.debug('\n%s', '=' * 60)
        with open('test/data/roster-parse.pkl', 'rb') as expf:
            expected = pickle.load(expf)
            observed = parse('test/data/roster.dat')
            self.assertEqual(observed, expected)


if __name__ == '__main__':
    unittest.main()
