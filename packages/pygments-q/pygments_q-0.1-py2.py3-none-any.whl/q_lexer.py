# -*- coding: utf-8 -*-
"""
    pygments.lexers.q
    ~~~~~~~~~~~~~~~~~

    Lexer for the q language.
"""

import re

from pygments.lexer import RegexLexer, include, bygroups, default, combined, \
    words
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Error, Whitespace, Literal
from pygments.util import get_bool_opt, get_list_opt, iteritems

__all__ = ['QLexer']

q_symbol_re = r"\b[a-zA-Z0-9.][a-zA-Z0-9_.]*\b"
q_handle_re = r":[a-zA-Z0-9:_.\\/]*"
q_keywords = (
    'abs', 'acos', 'aj', 'aj0', 'all', 'and', 'any', 'asc', 'asin',
    'asof', 'atan', 'attr', 'avg', 'avgs', 'bin', 'binr',
    'ceiling', 'cols', 'cor', 'cos', 'count', 'cov', 'cross',
    'csv', 'cut', 'deltas', 'desc', 'dev',
    'differ', 'distinct', 'div', 'each', 'ej', 'enlist', 'eval', 'except',
    'exit', 'exp', 'fby', 'fills', 'first', 'fkeys', 'flip',
    'floor', 'get', 'getenv', 'group', 'gtime', 'hclose', 'hcount', 'hdel',
    'hopen', 'hsym', 'iasc', 'idesc', 'ij', 'in', 'insert',
    'inter', 'inv', 'key', 'keys', 'last', 'like', 'lj', 'ljf', 'load', 'log',
    'lower', 'lsq', 'ltime', 'ltrim', 'mavg', 'max', 'maxs', 'mcount',
    'md5', 'mdev', 'med', 'meta', 'min', 'mins', 'mmax', 'mmin',
    'mmu', 'mod', 'msum', 'neg', 'next', 'not', 'null', 'or',
    'over', 'parse', 'peach', 'pj', 'prd', 'prds', 'prev', 'prior',
    'rand', 'rank', 'ratios', 'raze', 'read0', 'read1', 'reciprocal',
    'reverse', 'rload', 'rotate', 'rsave', 'rtrim', 'save', 'scan', 'set',
    'setenv', 'show', 'signum', 'sin', 'sqrt', 'ss', 'ssr', 'string',
    'sublist', 'sum', 'sums', 'sv', 'system', 'tables', 'tan', 'til',
    'trim', 'type', 'uj', 'ungroup', 'union',
    'upper', 'upsert', 'value', 'var', 'view', 'views', 'vs', 'wavg', 'where',
    'within', 'wj', 'wj1', 'wsum', 'ww', 'xasc', 'xbar', 'xcol', 'xcols',
    'xdesc', 'xexp', 'xgroup', 'xkey', 'xlog', 'xprev', 'xrank')

q_types = ('boolean', 'byte', 'char', 'date', 'datetime', 'float', 'guid', 'int',
           'minute', 'long', 'month', 'real', 'second', 'short', 'symbol',
           'time', 'timespan', 'timestamp')

# date/time units
q_units = ('dd', 'hh', 'uu', 'mm', 'week', 'year')
# words that we autocomplete, but probably don't want to highlight
q_misc = ('asize', 'bsize', 'depth', 'http', 'nbbo', 'price', 'trade', )
#
q_statements = ('do', 'if', 'while')


class QLexer(RegexLexer):
    """
    For `Q language<http://www.kx.com>`_ source code.

    """
    name = 'Q'
    aliases = ['q']
    filenames = ['*.q']
    mimetypes = ['text/x-q', 'application/x-q']

    tokens = {
        'whitespace': [
            (r'\n', Text),
            (r'\s+', Text),
            (r'\n ', Text),  # line continuation
            (r'/\n(.|\n)*?\n\\(\n|$)', Comment.Multiline),
            (r'/.*\n', Comment.Single),
        ],
        'statements': [
            (r'"[^\\"\n]"', String.Char),
            (r'"', String, 'string'),
            (r'`(%s|%s)?' % (q_symbol_re, q_handle_re), String.Symbol),
            include('numbers'),
            include('datetime'),
            (r':', Operator),
            (r'(in|neg|and|or|not|mod|div)\b', Operator.Word),
            (r'[~+*%=<>&^|._#!@$,]', Operator),
            (r'[()\[\]{};]', Punctuation),
            (r'-', Operator),  # match after numbers
            (words(q_keywords, suffix=r'\b'), Keyword),
            (words(('select', 'exec', 'update', 'delete'), suffix=r'\b'), Keyword.Declaration),
            (words(('from', 'by'), suffix=r'\b'), Keyword.Namespace),
            (r'[a-zA-Z][\w]*', Name),
        ],
        'root': [
            # q allows a file to start with a shebang
            (r'#!(.*?)$', Comment.Preproc),
            # (r'[^/"]+', Text),
            include('whitespace'),
            default('statement'),
        ],
        'statement': [
            include('whitespace'),
            include('statements'),
            ('[{}]', Punctuation),
            (';', Punctuation, '#pop'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\nrt"]|[0-7]{3})', String.Escape),
            (r'[^\\"\n]+', String),  # all other characters
        ],
        'datetime': [
            (r'\d\d:\d\d(:\d\d)?(\.\d+)?[tn]?', Literal.Date),
            (r'\d\d\d\d\.\d\dm', Literal.Date),
            (r'\d\d\d\d\.\d\d.\d\d', Literal.Date),
            (r'\d\d\d\d\.\d\d.\d\d[TD]', Literal.Date),
            (r'-?\d+[tzmunp]\b', Literal.Date),
            (r'0N[pmdznuvt]\b', Literal.Date),
        ],
        'numbers': [
            (r'[01]+b', Number.Bin),
            (r'-?0[nw][ef]?\b', Number.Float),
            (r'-?0[NW][ef]\b', Number.Float),
            (r'(-?\d+\.\d*|-?\d*\.\d+)([eE][+-]?[0-9]+)?[ef]?', Number.Float),
            (r'-?\d+[eE][+-]?[0-9]+[ef]?', Number.Float),
            (r'-?\d+[ef]', Number.Float),
            # (r'0[0-7]+j?', Number.Oct),
            # (r'0[bB][01]+', Number.Bin),
            (r'0x[a-fA-F0-9]+', Number.Hex),
            # (r'\d+L', Number.Integer.Long),
            (r'-?\d+[hij]?\b', Number.Integer),
            (r'0N[ghij]?\b', Number.Integer),
        ],
    }
