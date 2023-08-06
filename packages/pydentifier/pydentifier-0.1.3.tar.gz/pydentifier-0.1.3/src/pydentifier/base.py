import re

FIRST_CHAR_RANGE = 'A-Za-z_'
OTHER_CHAR_RANGE = 'A-Za-z_0-9'

NAME_RE = re.compile(r'^[{}][{}]*$'.format(FIRST_CHAR_RANGE, OTHER_CHAR_RANGE))

def upper_case_first_char(string):
    return string[:1].upper() + string[1:]
