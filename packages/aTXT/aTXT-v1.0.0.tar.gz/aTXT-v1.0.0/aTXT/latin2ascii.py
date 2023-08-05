#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: usuario
# @Date:   2014-09-14 17:02:20
# @Last Modified by:   Jonathan Prieto 
# @Last Modified time: 2014-10-07 14:42:00

from unicodedata import normalize, combining
from unidecode import *
from kitchen.text.converters import to_unicode
import sys

__version__ = "0.1"
__all__ = ["latin2ascii", "remove_accents"]

LATIN2ASCII = {
    # 0x00a0: '',
    # 0x00a7: '',

    # iso-8859-1
    0x00c0: 'A`',
    0x00c1: "A'",
    0x00c2: 'A^',
    0x00c3: 'A~',
    0x00c4: 'A:',
    0x00c5: 'A%',
    0x00c6: 'AE',
    0x00c7: 'C,',
    0x00c8: 'E`',
    0x00c9: "E'",
    0x00ca: 'E^',
    0x00cb: 'E:',
    0x00cc: 'I`',
    0x00cd: "I'",
    0x00ce: 'I^',
    0x00cf: 'I:',
    0x00d0: "D'",
    0x00d1: 'N~',
    0x00d2: 'O`',
    0x00d3: "O'",
    0x00d4: 'O^',
    0x00d5: 'O~',
    0x00d6: 'O:',
    0x00d8: 'O/',
    0x00d9: 'U`',
    0x00da: "U'",
    0x00db: 'U~',
    0x00dc: 'U:',
    0x00dd: "Y'",
    0x00df: 'ss',

    0x00e0: 'a`',
    0x00e1: "a'",
    0x00e2: 'a^',
    0x00e3: 'a~',
    0x00e4: 'a:',
    0x00e5: 'a%',
    0x00e6: 'ae',
    0x00e7: 'c,',
    0x00e8: 'e`',
    0x00e9: "e'",
    0x00ea: 'e^',
    0x00eb: 'e:',
    0x00ec: 'i`',
    0x00ed: "i'",
    0x00ee: 'i^',
    0x00ef: 'i:',
    0x00f0: "d'",
    0x00f1: 'n~',
    0x00f2: 'o`',
    0x00f3: "o'",
    0x00f4: 'o^',
    0x00f5: 'o~',
    0x00f6: 'o:',
    0x00f8: 'o/',
    0x00f9: 'o`',
    0x00fa: "u'",
    0x00fb: 'u~',
    0x00fc: 'u:',
    0x00fd: "y'",
    0x00ff: 'y:',

    # Ligatures
    0x0152: 'OE',
    0x0153: 'oe',
    0x0132: 'IJ',
    0x0133: 'ij',
    0x1d6b: 'ue',
    0xfb00: 'ff',
    0xfb01: 'fi',
    0xfb02: 'fl',
    0xfb03: 'ffi',
    0xfb04: 'ffl',
    0xfb05: 'ft',
    0xfb06: 'st',

    # Symbols
    # 0x2013: '',
    0x2014: '--',
    0x2015: '||',
    0x2018: '`',
    0x2019: "'",
    0x201c: '``',
    0x201d: "''",
    # 0x2022: '',
    # 0x2212: '',
}


def latin2ascii(s):
    try:
        s = ''.join(LATIN2ASCII.get(ord(c), c) for c in s)
    except:
        pass
    return s


def remove_accents(s):
    try:
        nkfd_form = normalize('NFKD', unicode(s))
        s = u''.join([c for c in nkfd_form if not combining(c)])
    except Exception, e:
        self._debug(remove_accents, e, s)
    return s

def enconding_path(s):
    if sys.platform in ["darwin"]:
        s = to_unicode(s)
        try:
            s = s.encode('utf-8', 'replace')
        except:
            pass
    elif sys.platform in ["win32"]:
        s = to_unicode(s, 'utf-8')
        # s = s.encode('utf-8', 'replace')
    return s