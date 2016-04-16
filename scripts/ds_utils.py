import re

def to_hex(data):
    return ":".join("{:02x}".format(ord(c)) for c in data)

def to_unicode(sjis):
    out = sjis
    out = re.sub("\x03", "[@]", out)
    out = re.sub("\x81\x64", "[..]", out)
    out = re.sub("\x81\x63", "[...]", out)
    out = out.decode("shift_jisx0213").encode("utf-8")
    return out

_SJIS_TABLE = {
    ' ': '\x81\x40',
    '!': '\x81\x49',
    '"': None,  # Use ` and '
    '#': '\x81\x94',
    '$': None,
    '%': '\x81\x93',
    '&': '\x81\x95',
    '\'': '\x81\x66',
    '(': '\x81\x69',
    ')': '\x81\x0A',
    '*': '\x81\x96',
    '+': '\x81\x7B',
    ',': '\x81\x43',
    '-': '\x81\x7C',
    '.': '\x81\x44',
    '/': '\x81\x5E',
    '0': '\x82\x4F',
    '1': '\x82\x50',
    '2': '\x82\x51',
    '3': '\x82\x52',
    '4': '\x82\x53',
    '5': '\x82\x54',
    '6': '\x82\x55',
    '7': '\x82\x56',
    '8': '\x82\x57',
    '9': '\x82\x58',
    ':': '\x81\x46',
    ';': '\x81\x47',
    '<': '\x81\x83',
    '=': '\x81\x81',
    '>': '\x81\x84',
    '?': '\x81\x48',
    '@': '\x81\x97',
    'A': '\x82\x60',
    'B': '\x82\x61',
    'C': '\x82\x62',
    'D': '\x82\x63',
    'E': '\x82\x64',
    'F': '\x82\x65',
    'G': '\x82\x66',
    'H': '\x82\x67',
    'I': '\x82\x68',
    'J': '\x82\x69',
    'K': '\x82\x6A',
    'L': '\x82\x6B',
    'M': '\x82\x6C',
    'N': '\x82\x6D',
    'O': '\x82\x6E',
    'P': '\x82\x6F',
    'Q': '\x82\x70',
    'R': '\x82\x71',
    'S': '\x82\x72',
    'T': '\x82\x73',
    'U': '\x82\x74',
    'V': '\x82\x75',
    'W': '\x82\x76',
    'X': '\x82\x77',
    'Y': '\x82\x78',
    'Z': '\x82\x79',
    '[': '\x81\x6D',
    '\\': '\x81\x5F',
    ']': '\x81\x6E',
    '^': '\x81\x68',
    '_': '\x81\x51',
    '`': '\x81\x67',
    'a': '\x82\x81',
    'b': '\x82\x82',
    'c': '\x82\x83',
    'd': '\x82\x84',
    'e': '\x82\x85',
    'f': '\x82\x86',
    'g': '\x82\x87',
    'h': '\x82\x88',
    'i': '\x82\x89',
    'j': '\x82\x8A',
    'k': '\x82\x8B',
    'l': '\x82\x8C',
    'm': '\x82\x8D',
    'n': '\x82\x8E',
    'o': '\x82\x8F',
    'p': '\x82\x90',
    'q': '\x82\x91',
    'r': '\x82\x92',
    's': '\x82\x93',
    't': '\x82\x94',
    'u': '\x82\x95',
    'v': '\x82\x96',
    'w': '\x82\x97',
    'x': '\x82\x98',
    'y': '\x82\x99',
    'z': '\x82\x9A',
    '{': '\x81\x6F',
    '|': '\x81\x62',
    '}': '\x81\x70',
    '~': '\x81\x60',
}

def to_sjis(ucstr):
    try:
        sjis = ucstr.decode("utf-8")
        sjis = re.sub(r"\[@\]", u"\x03", sjis)
        sjis = re.sub(r"\[..\]", u"\u2026", sjis)
        sjis = re.sub(r"\[...\]", u"\u2025", sjis)
        sjis = sjis.encode("shift_jisx0213")
        retstrs = []
        itr = iter(xrange(len(sjis)))
        for i in itr:
            b = ord(sjis[i])
            if b == ord('|'):
                ns = "%"
                for i in xrange(3):
                    ns += sjis[next(itr)]
                if ns == "%NUM":
                    try:
                        ns += sjis[next(itr)]
                    except:
                        pass
                retstrs.append(ns)
            elif b < 32:
                retstrs.append(sjis[i])
            elif b < 127:
                retstrs.append(_SJIS_TABLE[sjis[i]])
            else:
                retstrs.append(sjis[i] + sjis[i + 1])
                next(itr)

    except:
        print to_hex(sjis)
        print to_hex(''.join(retstrs))
        raise

    return ''.join(retstrs)
