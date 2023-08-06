import keyword

import six

from pydentifier import en
from pydentifier.base import NAME_RE, upper_case_first_char

class InvalidIdentifier(Exception):
    pass

def lower_underscore(string, prefix='', suffix=''):
    """
    Generate an underscore-separated lower-case identifier, given English text,
    a prefix, and an optional suffix.

    Useful for function names and variable names.

    `prefix` can be set to `''`, though be careful - without a prefix, the
    function will throw `InvalidIdentifier` when your string starts with a
    number.

    Example:
        >>> lower_underscore("This is an identifier", prefix='')
        'this_is_an_identifier'
    """

    return require_valid(append_underscore_if_keyword('_'.join(
        word.lower()
        for word in en.words(' '.join([prefix, string, suffix])))
    ))

def upper_underscore(string, prefix='', suffix=''):
    """
    Generate an underscore-separated upper-case identifier.
    Useful for constants.

    Takes a string, prefix, and optional suffix.

    `prefix` can be set to `''`, though be careful - without a prefix, the
    function will throw `InvalidIdentifier` when your string starts with a
    number.

    Example:
        >>> upper_underscore("This is a constant", prefix='')
        'THIS_IS_A_CONSTANT'
    """

    return require_valid(append_underscore_if_keyword('_'.join(
        word.upper()
        for word in en.words(' '.join([prefix, string, suffix])))
    ))

def upper_camel(string, prefix='', suffix=''):
    """
    Generate a camel-case identifier with the first word capitalised.
    Useful for class names.

    Takes a string, prefix, and optional suffix.

    `prefix` can be set to `''`, though be careful - without a prefix, the
    function will throw `InvalidIdentifier` when your string starts with a
    number.

    Example:
        >>> upper_camel("I'm a class", prefix='')
        'IAmAClass'
    """

    return require_valid(append_underscore_if_keyword(''.join(
        upper_case_first_char(word)
        for word in en.words(' '.join([prefix, string, suffix])))
    ))

def lower_camel(string, prefix='', suffix=''):
    """
    Generate a camel-case identifier.
    Useful for unit test methods.

    Takes a string, prefix, and optional suffix.

    `prefix` can be set to `''`, though be careful - without a prefix, the
    function will throw `InvalidIdentifier` when your string starts with a
    number.

    Example:
        >>> lower_camel("User can login", prefix='test')
        'testUserCanLogin'
    """

    return require_valid(append_underscore_if_keyword(''.join(
        word.lower() if index == 0 else upper_case_first_char(word)
        for index, word in enumerate(en.words(' '.join([prefix, string, suffix]))))
    ))

def append_underscore_if_keyword(identifier):
    """
    If identifier is not a Python keyword, return it as-is.
    Otherwise, return the identifier with an underscore appended.
    """

    if keyword.iskeyword(identifier):
        return identifier + '_'
    else:
        return identifier

def is_valid(identifier):
    """
    If the identifier is valid for Python, return True, otherwise False.
    """

    return (
        isinstance(identifier, six.string_types)
        and bool(NAME_RE.search(identifier))
        and not keyword.iskeyword(identifier)
    )

def require_valid(identifier):
    """
    If the identifier is valid for Python, return it as-is, otherwise raise
    an `InvalidIdentifier` exception.
    """

    if not is_valid(identifier):
        raise InvalidIdentifier('Invalid Python identifier {!r}'.format(identifier))
    else:
        return identifier
