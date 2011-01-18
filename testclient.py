#!/usr/bin/env python

import xmlrpclib

p = xmlrpclib.ServerProxy("http://localhost:8000/")

# Well-formed requests
assert p.upper('foo bar') == 'FOO BAR'
assert p.upper(u'foo\u2026bar') == u'FOO\u2026BAR'
assert p.upper('foo\x0abar') == 'FOO\x0aBAR'

# Non well-formed requests with control characters that aren't allowed in XML
assert p.upper('foo\x01bar') == 'FOOBAR'
assert p.upper(u'\u2026foo\x01bar') == u'\u2026FOOBAR'
assert p.upper('\0\x7f\x80\x85') == u'\x7f\u20ac\u2026'
