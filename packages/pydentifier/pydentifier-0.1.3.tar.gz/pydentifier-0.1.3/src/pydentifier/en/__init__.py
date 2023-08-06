import re

import six

from pydentifier.base import OTHER_CHAR_RANGE, upper_case_first_char
from pydentifier.en.contractions import CONTRACTIONS

CONTRACTION_RE = re.compile(r'(?i)(^|\W)({})(?=\W|$)'.format('|'.join(
    re.escape(contraction)
    for contraction in six.iterkeys(CONTRACTIONS)
)))

NON_NAME_NON_WHITESPACE_RE = re.compile(r'([^{}\s])'.format(OTHER_CHAR_RANGE))

LETTER_RE = re.compile(r'[A-Za-z]')

def words(string):
    string = expand_contractions(string)
    string = NON_NAME_NON_WHITESPACE_RE.sub(r' ', string)
    return string.split()

def expand_contractions(string):
    def replace_contraction(match):
        prefix, contraction = match.groups()
        expansion = CONTRACTIONS[contraction.lower()]
        if LETTER_RE.search(contraction).group().isupper():
            expansion = upper_case_first_char(expansion)
        return prefix + expansion

    return CONTRACTION_RE.sub(replace_contraction, string)
