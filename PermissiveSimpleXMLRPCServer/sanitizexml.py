import re

from BeautifulSoup import UnicodeDammit

def sanitize_xml(data, log=None):
    u"""Take a string of bytes or unicode representing XML data and turn it into a UTF-8 string with characters that are invalid in that version of XML removed.

    >>> sanitize_xml("<?xml encoding='UTF-8'?><hello>hi</hello>")
    '<?xml encoding="UTF-8"?><hello>hi</hello>'
    >>> sanitize_xml(u"<?xml encoding='UTF-8'?><hello>hi</hello>")
    '<?xml encoding="UTF-8"?><hello>hi</hello>'
    >>> sanitize_xml("<?xml encoding='UTF-16'?><hello>hi</hello>")
    '<?xml encoding="UTF-8"?><hello>hi</hello>'
    >>> sanitize_xml('<?xml encoding="UTF-16"?><hello>hi</hello>')
    '<?xml encoding="UTF-8"?><hello>hi</hello>'
    >>> sanitize_xml('<?xml encoding="blah"?><hello>hi</hello>')
    '<?xml encoding="UTF-8"?><hello>hi</hello>'
    >>> sanitize_xml('<?xml encoding="blah" ?><hello>hi</hello>')
    '<?xml encoding="UTF-8"?><hello>hi</hello>'

    >>> sanitize_xml('<?xml version="1.0" encoding="blah" ?><hello>hi</hello>')
    '<?xml version="1.0" encoding="UTF-8"?><hello>hi</hello>'
    >>> sanitize_xml('<?xml version="1.1" encoding="blah" ?><hello>hi</hello>')
    '<?xml version="1.1" encoding="UTF-8"?><hello>hi</hello>'
    >>> sanitize_xml('<hello>hi</hello>')
    '<?xml version="1.0" encoding="UTF-8"?><hello>hi</hello>'

    >>> sanitize_xml(u'\u2026')
    '<?xml version="1.0" encoding="UTF-8"?>\\xe2\\x80\\xa6'
    >>> sanitize_xml('hello\\x00world')
    '<?xml version="1.0" encoding="UTF-8"?>helloworld'
    >>> def log(msg): print msg
    ...
    >>> sanitize_xml('hello\\0world', log)
    Found first disallowed character u'\\x00' at position 44
    '<?xml version="1.0" encoding="UTF-8"?>helloworld'


    \x7f is allowed in XML 1.0, but not in XML 1.1

    >>> sanitize_xml(
    ... '<?xml version="1.0" encoding="UTF-8"?><hello>\\x7f</hello>')
    '<?xml version="1.0" encoding="UTF-8"?><hello>\\x7f</hello>'
    >>> sanitize_xml('<?xml version="1.1"?><hello>\\x7f</hello>', log)
    Found first disallowed character u'\\x7f' at position 46
    '<?xml version="1.1" encoding="UTF-8"?><hello></hello>'


    The \x80 in the following makes UnicodeDammit interpret the string using the
    windows-1252 encoding, so it gets translated into a Euro symbol.

    >>> sanitize_xml('hello\\x80world', log)
    '<?xml version="1.0" encoding="UTF-8"?>hello\\xe2\\x82\\xacworld'

    If we pass in a unicode string instead so that UnicodeDammit is bypassed
    then it gets properly ignored...

    >>> sanitize_xml(u'hello\u0080world', log).decode('utf_8')
    u'<?xml version="1.0" encoding="UTF-8"?>hello\\x80world'

    unless we use XML 1.1 where it is properly disallowed and so stripped:

    >>> sanitize_xml(u'<?xml version="1.1" ?>hello\u0080world', log)
    Found first disallowed character u'\\x80' at position 44
    '<?xml version="1.1" encoding="UTF-8"?>helloworld'
    """

    if isinstance(data, unicode):
        u = data
    else:
        u = UnicodeDammit(data, smartQuotesTo=None).unicode

    # The text may have a prolog that specifies a character encoding, but we're
    # going to re-encode it as UTF-8 so make sure the prolog reflects that.
    m = re.match("""^<\?xml[\s]*([^\?]*?)[\s]*\?>""", u)

    if not m:
        # no prolog found, so add one of our own
        u = '<?xml version="1.0" encoding="UTF-8"?>' + u
        version = 0
    else:
        new_encoding = 'encoding="UTF-8"'

        attr = m.group(1)

        encoding_m = re.search("""encoding[\s]*=[\s]*['"].*?['"]""", attr)
        if encoding_m: # replace the encoding
            attr = \
                attr[:encoding_m.start()] + \
                new_encoding + \
                attr[encoding_m.end():]
        else: # or add it if there wasn't one in the prolog already
            attr = attr + ' ' + new_encoding

        u = '<?xml ' + attr + '?>' + u[m.end():]

        # see if the prolog has a version number too
        m2 = re.search("""[\s]*version[\s]*=[\s]*['"](.*?)['"]""", attr)
        if m2:
            if m2.group(1) == u'1.0':
                version = 0
            else:
                # anything unknown is going to be >1.1, so assume the 1.1
                # invalid character rules
                version = 1
        else:
            # version number is optional for XML 1.0
            version = 0

    allowed = u'\x09\x0a\x0d\x20-\x7e\xa0-\ud7ff\ue000-\ufffd'

    if version == 0:
        allowed = allowed + u'\x7f-\x9f'
    else:
        allowed = allowed + u'\x85'

    disallowed = re.compile('[^' + allowed + ']')

    skip_replacement = False
    if log:
        m = disallowed.search(u)
        if m:
            log('Found first disallowed character %s at position %d' % (
                repr(m.group(0)), m.start() + 1))
        else:
            # no point searching again in a moment
            skip_replacement = True

    if not skip_replacement:
        u = disallowed.sub('', u)

    return u.encode('utf_8')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
