from pygments.formatter import Formatter

PYTEST_BEFORE = u'''\
def test_%s():
    fragment = %r
    tokens = [
'''
PYTEST_AFTER = u'''\
    ]
    assert tokens == list(lexer.get_tokens(fragment))
'''


class PytestFormatter(Formatter):
    """Format tokens as appropriate for a new pytest"""

    name = 'Pytest'
    aliases = ['pytest']

    def __init__(self, **options):
        Formatter.__init__(self, **options)
        if self.encoding is not None and self.encoding != 'utf-8':
            raise ValueError("Only None and utf-8 are allowed encodings.")
        self.testname = options.get('testname', 'needs_name')

    def format(self, tokensource, outfile):
        indentation = ' ' * 8
        rawbuf = []
        outbuf = []
        for ttype, value in tokensource:
            rawbuf.append(value)
            outbuf.append('%s(%s, %r),\n' % (indentation, ttype, value))

        before = PYTEST_BEFORE % (self.testname, u''.join(rawbuf),)
        during = u''.join(outbuf)
        after = PYTEST_AFTER
        if self.encoding is None:
            outfile.write(before + during + after)
        else:
            outfile.write(before.encode('utf-8'))
            outfile.write(during.encode('utf-8'))
            outfile.write(after.encode('utf-8'))
        outfile.flush()
