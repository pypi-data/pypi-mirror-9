# -*- coding: utf-8 -*-
"""
    pygments.lexers.q
    ~~~~~~~~~~~~~~~~~

    Lexer for the q language.
"""

import re

from pygments.lexer import RegexLexer, include, bygroups, default, combined, \
    words
from pygments.token import (Text, Comment, Operator, Keyword, Name, String,
    Number, Punctuation, Error, Whitespace, Literal, Error, STANDARD_TYPES)
from pygments.util import get_bool_opt, get_list_opt, iteritems
from pygments.filter import Filter, simplefilter



__all__ = ['QLexer']

q_eol_comment = r'(^|(?<=\s))/.*(?=(\n|$))'
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

Date = Literal.Date

# Q literals

Q_Boolean = Number.Bin.Q_Boolean
Q_Guid = Number.Integer.Long.Q_Guid
Q_Byte = Number.Hex.Q_Byte
Q_Short = Number.Integer.Q_Long.Q_Int.Q_Short
Q_Int = Number.Integer.Q_Long.Q_Int
Q_Long = Number.Integer.Q_Long
Q_Real = Number.Float.Q_Float.Q_Real
Q_Float = Number.Float.Q_Float
Q_Char = String.Char.Q_Char
Q_Symbol = String.Symbol.Q_Symbol
Q_Date = Date.Q_Date
Q_Timestamp = Q_Date.Q_Timestamp
Q_Month = Date.Q_Month
Q_Datetime = Q_Date.Q_Datetime
Q_Timespan = Date.Q_Timespan
Q_Minute = Date.Q_Time.Q_Second.Q_Minute
Q_Second = Date.Q_Time.Q_Second
Q_Time = Date.Q_Time

Q_LITERALS = {
    'b': Q_Boolean,
    'g': Q_Guid,
    'x': Q_Byte,
    'h': Q_Short,
    'i': Q_Int,
    'j': Q_Long,
    'e': Q_Real,
    'f': Q_Float,
    'c': Q_Char,
    's': Q_Symbol,
    'p': Q_Timestamp,
    'm': Q_Month,
    'd': Q_Date,
    'z': Q_Datetime,
    'n': Q_Timespan,
    'u': Q_Minute,
    'v': Q_Second,
    't': Q_Time,
}


class QFilter(Filter):
    """Filter to decorate Q literals with proper types"""
    def __init__(self, **options):
        Filter.__init__(self, **options)

    def token_type(self, ttype, value):
        """returns the q type of the token"""
        #import pdb; pdb.set_trace()
        if not (ttype in Number or ttype in Date):
            # Don't decorate tokens other than numbers or dates for now.
            return ttype
        if value in ['0n', '0w', '-0w']:
            return Q_Float
        if value.startswith('0x'):
            return Q_Byte
        rtype = Q_LITERALS.get(value[-1])
        if rtype is not None:
            return rtype
        if 'E' in value.upper():
            return Q_Float
        n = len(value)
        if n >= 10 and value[4] == value[7] == '.':
            # value starts with y.m.d
            if n == 10:
                return Q_Date
            return {
                'T': Q_Datetime,
                'D': Q_Timestamp
            }[value[10]]
        if 'D' in value:
            return Q_Timespan
        if ':' in value:
            return {
                5: Q_Minute,
                8: Q_Second,
            }.get(n, Q_Time)
        if '.' in value:
            return Q_Float
        if ttype is Number.Integer:
            return Q_Long

        return ttype

    def upcast(self, ttype, vtype, swapped=False):
        """upcast to "higher" type

        ttype - token type
        vtype - expected vector type

        returns "higher" type or Error
        """
        if ttype in vtype:
            result = vtype
        elif ttype in Number.Integer:
            result = vtype
        elif not swapped:
            result = self.upcast(vtype, ttype, swapped=True)
        else:
            result = Error

        return result

    def fix_types(self, nums):
        # check if we have type code on the last token
        vtype, nval = nums[-1]
        vtype = Q_LITERALS.get(nval[-1]) or vtype
        # Scan remaining tokens
        for token in nums[:-1]:
            ttype, value = token
            if value[-1] in Q_LITERALS and value != '0n':
                rtype = Error
            else:
                rtype = self.upcast(ttype, vtype)
            if rtype is Error:
                token[0] = Error
            else:
                vtype = rtype

        # Change type of all tokens
        for item in nums:
            if item[0] is not Error:
                item[0] = vtype

    def filter(self, lexer, stream):
        stream = iter(stream)
        nums = []
        toks = []
        while True:
            ttype, value = next(stream, (None, None))
            if ttype is not None:
               ttype = self.token_type(ttype, value)
            item = [ttype, value]
            # print(item)
            if ttype in Number or ttype in Date:
                nums.append(item)
                toks.append(item)
            elif ttype is Whitespace or ttype in Comment:
                toks.append(item)
            else:
                if len(nums) > 1:
                    self.fix_types(nums)

                # Yield modified tokens
                for mtype, mval in toks:
                    yield mtype, mval
                nums[:] = toks[:] = []
                # and the current token unless None
                if ttype is not None:
                    yield ttype, value
                else:
                    break  # the forever loop

@simplefilter
def standardize(self, lexer, stream, options):
    for ttype, value in stream:
        while ttype not in STANDARD_TYPES:
            ttype = ttype.parent
        yield ttype, value


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
            (r'[ \t]+', Whitespace),
            (r'\n[ \t]+', Whitespace),  # line continuation
            (r'/\n(.|\n)*?\n\\(\n|$)', Comment.Multiline),
            (q_eol_comment, Comment.Single),
        ],
        'statements': [
            (r'"[^\\"\n]"', String.Char),
            (r'"', String, 'string'),
            (r'`(%s|%s)?' % (q_symbol_re, q_handle_re), String.Symbol),
            include('datetime'),
            include('numbers'),
            (r':', Operator),
            (r'(in|neg|and|or|not|mod|div)\b', Operator.Word),
            (r'[~+*%=<>&^|._#!@$,/\\?]', Operator),
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
            ('[{}\n]', Punctuation),
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
            (r'\d\d\d\d\.\d\d.\d\d([TD](\d\d(:\d\d){0,2})?\.?\d*)?\b', Literal.Date),
            (r'-?\d+[tzmunp]\b', Literal.Date),
            (r'0N[pmdznuvt]\b', Literal.Date),
        ],
        'numbers': [
            (r'[01]+b', Number.Bin),
            (r'-?0[nw][ef]?\b', Number.Float),
            (r'-?0[NW][ef]\b', Number.Float),
            (r'(-?\d+\.\d*|-?\d*\.\d+)([eE][+-]?[0-9]+)?[ef]?\b', Number.Float),
            (r'-?\d+[eE][+-]?[0-9]+[ef]?\b', Number.Float),
            (r'-?\d+[ef]\b', Number.Float),
            (r'0x[a-fA-F0-9]+\b', Number.Hex),
            (r'(-?(\d+|0W)|0N)[hij]?\b', Number.Integer),
            (r'0Ng\b', Number.Integer),
        ],
    }

    def __init__(self, std=True, **options):
        RegexLexer.__init__(self, **options)
        filter = QFilter(**options)
        self.add_filter(filter, **options)
        if std:
            self.add_filter(standardize(**options), **options)
