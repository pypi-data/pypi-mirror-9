# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the Lesser GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
from __future__ import print_function, unicode_literals

import io
import logging
from collections import OrderedDict

import rply


# logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
# level=logging.DEBUG)

__version__ = '0.3.0'

__lg = rply.LexerGenerator()
__lg.add("OPBRACE", r'\{')
__lg.add("CLBRACE", r'\}')
__lg.add("OPBRAK", r'\[')
__lg.add("CLBRAK", r'\]')
__lg.add("RECSEP", r';')
__lg.add("STRING", r'"[^"]+"')
__lg.add("NUMBER", r'\d+')
__lg.add("RETURN", r'return')
__lg.add("BOOL", r'true|false')

__lg.ignore(r"[\s\t]+")
__lg.ignore(r'[=]')

lexer = __lg.build()

__pg = rply.ParserGenerator([rule.name for rule in lexer.rules],
                            cache_id='received_parser')


@__pg.production('main : RETURN dict')
def main(p):
    logging.debug('in = %s', p)
    logging.debug('out = %s', p[1])
    return p[1]


@__pg.production('dict : OPBRACE recs CLBRACE')
def parse_dict(p):
    logging.debug('in = %s', p)
    logging.debug('in = p[1] %s', p[1])
    if p[1][0]:
        logging.debug('out = %s', OrderedDict(p[1]))
        return OrderedDict(p[1])


@__pg.production('recs : rec')
@__pg.production('recs : rec recs')
def parse_recs(p):
    logging.debug('in = %s', p)
    if len(p) > 1:
        out = [p[0]]
        out.extend(p[1])
        logging.debug('out = %s', out)
        return out

    logging.debug('out = %s', p)
    return p


@__pg.production('rec : OPBRAK value CLBRAK value RECSEP')
@__pg.production('rec : ')
def parse_rec(p):
    # Empty dictionary may happen
    if p:
        logging.debug('in = %s', p)
        logging.debug('out = %s', str((p[1], p[3])))
        return p[1], p[3]


def process_token(tok):
    if tok.gettokentype() == u'STRING':
        #logging.debug('Cleaning STRING')
        logging.debug('out = %s', tok.getstr().strip('"'))
        return tok.getstr().strip('"')
    elif tok.gettokentype() == u'NUMBER':
        logging.debug('out = %s', int(tok.getstr()))
        return int(tok.getstr())
    elif tok.gettokentype() == u'BOOL':
        strval = tok.getstr().lower()
        logging.debug('out = %s', str(strval == 'true'))
        if strval == 'true':
            return True
        elif strval == 'false':
            return False
        else:
            ValueError('Wrong Boolean value: %s', strval)
    else:
        logging.debug('out = %s', tok.getstr())
        return tok.getstr()


@__pg.production('value : STRING')
@__pg.production('value : NUMBER')
@__pg.production('value : BOOL')
@__pg.production('value : dict')
@__pg.production('value : ')
def parse_value(p):
    logging.debug('in = %s', p)
    if p:
        if isinstance(p[0], rply.Token):
            return process_token(p[0])
        else:
            logging.debug('out = %s', p[0])
            return p[0]
    logging.debug('out = nothing')
    return None


@__pg.error
def error_handler(token):
    raise ValueError(
        "Ran into a %s where it was't expected" % token.gettokentype())


parser = __pg.build()


def parse(infile):
    try:
        filename_given = isinstance(infile, basestring)
    except NameError:
        filename_given = isinstance(infile, str)
    if filename_given:
        infile = io.open(infile, encoding='utf8')

    str2parse = infile.read()

    if filename_given:
        infile.close()

    return parser.parse(lexer.lex(str2parse))
