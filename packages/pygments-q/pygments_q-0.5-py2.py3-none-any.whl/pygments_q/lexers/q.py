# -*- coding: utf-8 -*-
"""
    pygments.lexers.q
    ~~~~~~~~~~~~~~~~~

    Lexer for the q language.
"""

from pygments.lexer import RegexLexer, include, default, words, bygroups, using
from pygments.lexers.shell import BashLexer
from pygments.token import (Comment, Operator, Keyword, Name, String, Generic,
                            Number, Punctuation, Whitespace, Literal, Error, STANDARD_TYPES,
                            Text, Escape, Token)
from pygments.filter import Filter, simplefilter

__all__ = ['QLexer']

q_eol_comment = r'(^|(?<=\s))/.*(?=(\n|$))'
q_name_re = r'[a-zA-Z][\w]*'
q_symbol_re = r"[a-zA-Z0-9.][a-zA-Z0-9_.:]*"
q_handle_re = r":[a-zA-Z0-9:_.\\/]*"
q_keywords = (
    'abs', 'acos', 'aj', 'aj0', 'all', 'any', 'asc', 'asin',
    'atan', 'attr', 'avg', 'avgs',
    'ceiling', 'cols', 'cos', 'count',
    'csv', 'deltas', 'desc', 'dev',
    'differ', 'distinct', 'ej', 'enlist', 'eval',
    'exit', 'exp', 'fills', 'first', 'fkeys', 'flip',
    'floor', 'get', 'getenv', 'group', 'gtime', 'hclose', 'hcount', 'hdel',
    'hopen', 'hsym', 'iasc', 'idesc',
    'inv', 'key', 'keys', 'last', 'load', 'log',
    'lower', 'ltime', 'ltrim', 'max', 'maxs',
    'md5', 'med', 'meta', 'min', 'mins',
    'neg', 'not', 'next', 'null',
    'parse', 'prd', 'prds', 'prev',
    'rand', 'rank', 'ratios', 'raze', 'read0', 'read1', 'reciprocal',
    'reverse', 'rload', 'rsave', 'rtrim', 'save',
    'show', 'signum', 'sin', 'sqrt', 'ssr', 'string',
    'sum', 'sums', 'system', 'tables', 'tan', 'til',
    'trim', 'type', 'ungroup',
    'upper', 'value', 'var', 'view', 'views', 'where',
    'wj', 'wj1', 'ww')

q_types = ('boolean', 'byte', 'char', 'date', 'datetime', 'float', 'guid', 'int',
           'minute', 'long', 'month', 'real', 'second', 'short', 'symbol',
           'time', 'timespan', 'timestamp')

q_word_operators = (
    'in', 'div', 'bin', 'binr',
    'and', 'asof', 'cor', 'cov', 'cross', 'cut', 'each', 'except',
    'fby', 'ij', 'insert', 'inter', 'like', 'lj', 'ljf', 'lsq', 'mavg', 'mcount', 'mdev',
    'mmax', 'mmin', 'mmu', 'mod', 'msum', 'or', 'over', 'peach', 'pj',
    'prior', 'rotate', 'scan', 'set', 'setenv', 'ss', 'sublist', 'sv', 'union',
    'uj', 'upsert', 'vs', 'wavg', 'within', 'wsum', 'xasc',
    'xbar', 'xcol', 'xcols', 'xdesc', 'xgroup', 'xkey', 'xlog', 'xprev',
    'xrank')

q_dotz = (
    "D",
    "K",
    "N",
    "P",
    "T",
    "W",
    "Z",
    "a",
    "b",
    "d",
    # "exit",
    "f",
    "h",
    "i",
    "k",
    "l",
    "n",
    "o",
    "p",
    "pc",
    "pg",
    "ph",
    "pi",
    "po",
    "pp",
    "ps",
    "pw",
    "q",
    # "s",  - valid only in lambdas
    "t",
    "ts",
    "u",
    "vs",
    "w",
    "x",
    "z",
)

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
        # import pdb; pdb.set_trace()
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
        'expression': [
            (r'"[^\\"\n]"', String.Char),
            (r'"', String, 'string'),
            (r'`(%s|%s)?' % (q_symbol_re, q_handle_re), String.Symbol),
            (words([r'.z.' + z for z in q_dotz], suffix=r'\b'), Keyword),
            (r'\.z\.\w+', Error),
            (r'\.{n}\.{n}'.format(n=q_name_re), Name.Variable.Global),
            include('datetime'),
            (r'[012]:', Operator.Word),
            include('numbers'),
            (words(q_word_operators, suffix=r'\b'), Operator.Word),
            (r':', Operator),
            (r"[~+*%=<>&^|._#!@$,/\\?']", Operator),
            (r'[()\[\];]', Punctuation),
            (r'-', Operator),  # match after numbers
            (words(q_keywords, suffix=r'\b'), Keyword),
            (words(('select', 'exec', 'update', 'delete'), suffix=r'\b'), Keyword.Declaration),
            (words(('from', 'by'), suffix=r'\b'), Keyword.Namespace),
            (q_name_re, Name),
        ],
        'root': [
            # q allows a file to start with a shebang
            (r'^#!(.*?)\n', Comment.Preproc),
            # q) - switch language to q
            (r'^q\)', Generic.Prompt, "q"),
            # k) - switch language to k
            (r'^k\)', Generic.Prompt, "k"),
            # Don't highlight text following unsupported prompt
            (r'^(\w\))(.*)(\n)', bygroups(Generic.Prompt, Text, Punctuation)),
            # System commands, shell escape or end comments
            (r'^\\', Escape, 'escape'),
            include('whitespace'),
            (r'^\n', Punctuation),    # should this be Whitespace?
            default('statement-global'),
        ],
        'escape': [
            (r'(?<=^\\)\n(?s).*', Comment.Multiline),
            (r'(?<=^\\)([abBcCdeglopPrsSTuvwWxz12_]|cd)\b(.*)', bygroups(Keyword.Reserved, Text)),
            (r'(?<=^\\)ts?\b', Keyword.Reserved, 'qq'),  # continue with regular highlighting
            (r'(?<=^\\)\w\w+.*$', using(BashLexer)),
            (r'(?<=^\\).\b', Error, '#pop'),
            (r'\n', Punctuation, '#pop'),
        ],
        'args': [
            include('whitespace'),
            (q_name_re, Name.Variable),
            (';', Punctuation),
            (r'\]', Punctuation, ('#pop', 'statement-in-lambda')),
        ],
        'qq': [
            (r'\n', Whitespace, ('#pop', ) * 2),
            include('statement'),
        ],
        'q': [
            (r'\n', Whitespace, '#pop'),
            include('statement'),
        ],
        'k': [
            (r'\n', Whitespace, '#pop'),
            (r'[^\n]+', Text),  # don't parse k for now
        ],
        'statement': [
            include('whitespace'),
            include('expression'),
            (r'(\{)(\s*)(\[)', bygroups(Punctuation, Whitespace, Punctuation), 'args'),
            (r'\{', Punctuation, 'statement-in-lambda'),
            # NB: line continuation is handled in whitespace rules
            (r';', Punctuation),
            # end a statement on a brace and pop out of lambda
            (r'\}', Punctuation, '#pop'),
        ],
        'statement-global': [
            (r'(%s)(\s*)(::?)' % q_name_re, bygroups(Name.Variable.Global, Whitespace, Operator)),
            (r'\.z\.s\b', Error),
            include('statement'),
            (r'\n', Punctuation, '#pop'),
        ],
        'statement-in-lambda': [
            # ignore all whitespace inside {} - may miss some errors
            (r'\s+', Whitespace),
            # global variable assignment
            (r'(%s)(\s*)(::)' % q_name_re, bygroups(Name.Variable.Global, Whitespace, Operator)),
            # local variable assignment
            (r'(%s)(\s*)(:)' % q_name_re, bygroups(Name.Variable, Whitespace, Operator)),
            (r'\.z\.s\b', Keyword),
            include('statement'),
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
            (r'(0N|-?0W)[pmdznuvt]\b', Literal.Date),
        ],
        'numbers': [
            (r'[01]+b', Number.Bin),
            (r'(0n|-?0w)[ef]?\b', Number.Float),
            (r'(0N|-?0W)[ef]\b', Number.Float),
            (r'(-?\d+\.\d*|-?\d*\.\d+)([eE][+-]?[0-9]+)?[ef]?\b', Number.Float),
            (r'-?\d+[eE][+-]?[0-9]+[ef]?\b', Number.Float),
            (r'-?\d+[ef]\b', Number.Float),
            (r'0x[a-fA-F0-9]+\b', Number.Hex),
            (r'(-?(\d+|0W)|0N)[hij]?(?=(_|\b))', Number.Integer),
            (r'0Ng\b', Number.Integer),
        ],
    }

    def __init__(self, std=True, **options):
        RegexLexer.__init__(self, **options)
        filter = QFilter(**options)
        self.add_filter(filter, **options)
        if std and 'unfiltered' not in options:
            self.add_filter(standardize(**options), **options)
