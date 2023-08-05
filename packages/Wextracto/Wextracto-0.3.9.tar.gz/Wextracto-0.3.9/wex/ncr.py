import re


ncr_replacements = {
    0x00: 0xFFFD,
    0x0D: 0x000D,
    0x80: 0x20AC,
    0x81: 0x0081,
    0x81: 0x0081,
    0x82: 0x201A,
    0x83: 0x0192,
    0x84: 0x201E,
    0x85: 0x2026,
    0x86: 0x2020,
    0x87: 0x2021,
    0x88: 0x02C6,
    0x89: 0x2030,
    0x8A: 0x0160,
    0x8B: 0x2039,
    0x8C: 0x0152,
    0x8D: 0x008D,
    0x8E: 0x017D,
    0x8F: 0x008F,
    0x90: 0x0090,
    0x91: 0x2018,
    0x92: 0x2019,
    0x93: 0x201C,
    0x94: 0x201D,
    0x95: 0x2022,
    0x96: 0x2013,
    0x97: 0x2014,
    0x98: 0x02DC,
    0x99: 0x2122,
    0x9A: 0x0161,
    0x9B: 0x203A,
    0x9C: 0x0153,
    0x9D: 0x009D,
    0x9E: 0x017E,
    0x9F: 0x0178,
}

LT = b'<'
GT = b'>'
AMP = b'&'
SLASH = b'/'
HASH = b'#'

cdata_tags = (b'script', b'style')

class InvalidNumCharRefReplacer(object):
    """ Replaces invalid numeric character references in HTML.

    In the wild you can find HTML containing numeric character
    references where the numbers are not valid Unicode characters.
    Most often the numbers are windows-1252 characters.
    So we replace this invalid characters as best we can.
    Note that the Python 3 html.parser.HTMLParser also does this
    and so does the html5lib HTML parser.
    """

    def __init__(self, fp):
        self.fp = fp
        self.clean = b''
        self.dirty = b''
        self.cdata_tag = None

    def read(self, size=None):
        while True:
            dirty = self.fp.read(size)
            eof = (size is None or not dirty)
            dirty = self.dirty + dirty
            clean, self.dirty, self.cdata_tag = clean_ncr(dirty,
                                                          eof,
                                                          self.cdata_tag)
            self.clean += clean
            if eof:
                assert not self.dirty
                data = self.clean
                self.clean = b''
                return data
            elif len(self.clean) >= size:
                data = self.clean[:size]
                self.clean = self.clean[size:]
                return data


def clean_ncr(dirty, eof, cdata_tag=None):
    parts = []
    # tokenize 'dirty' looking for start tags and numeric character references
    pos = 0
    # position of start of next part
    part_pos = 0

    assert not cdata_tag or cdata_tag == cdata_tag.lower().strip()

    end_token = {
        AMP: end_char_ref,
        LT: end_tag,
    }

    while True:

        if cdata_tag:
            # ignore char refs inside <script> or <style> tags.
            # just looking for </script> or </style>
            begin_token = begin_tag
        else:
            begin_token = begin_tag_or_char_ref

        begin = begin_token.search(dirty, pos)
        if not begin:
            # now we know there are not more tokens in this chunk
            pos = len(dirty)
            break

        token = end_token[begin.group()].search(dirty, begin.end())
        if not token:
            # We haven't seen the end of this token yet,
            # we may be called again, but with more data (if !eof).
            break

        if begin.group() == LT:
            if token.group(1) == SLASH and cdata_tag:
                tag = token.group(2).lower()
                if tag == cdata_tag:
                    cdata_tag = None
            else:
                tag = token.group(2).lower()
                if not cdata_tag and tag in cdata_tags:
                    cdata_tag = tag
        else:
            assert begin.group() == AMP
            assert not cdata_tag

            ncr = token.group(1)
            if ncr:
                if ncr.lower().startswith(b'x'):
                    code_point = int(ncr[1:], 16)
                else:
                    code_point = int(ncr, 10)

                if code_point in ncr_replacements:
                    parts.append(dirty[part_pos:begin.start()])
                    ncr = u'&#x%0X' % ncr_replacements[code_point]
                    parts.append(ncr.encode('ascii'))
                    part_pos = token.end()

        pos = token.end()

    if eof:
        parts.append(dirty[part_pos:])
        pos = len(dirty)
    else:
        parts.append(dirty[:pos])

    return b''.join(parts), dirty[pos:], cdata_tag

#
# When scanning for the begining of tokens we look just one character
# at a time so that we don't have to worry about partial buffering.
begin_tag = re.compile(LT)
begin_tag_or_char_ref = re.compile(b'[<&]', re.I)
end_tag = re.compile(b'(/?)\s*([a-z]+)(?=[^a-z])', re.I)
end_char_ref = re.compile(b'[^#]|#(x[0-9A-F]+|[0-9]+)', re.I)


def replace_invalid_ncr(fp):
    return InvalidNumCharRefReplacer(fp)
