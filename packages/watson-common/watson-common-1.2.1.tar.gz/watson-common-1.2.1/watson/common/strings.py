# -*- coding: utf-8 -*-
import re
import unicodedata


def hash(string, replace='_', titlecase=False):
    """Replaces characters with dashes.

    Args:
        replace (string): The character to replace
        titlecase (bool): Titlecase every word
    """
    if titlecase:
        string = string.lower().replace(replace, ' ').title()
        replace = ' '
    return string.replace(replace, '-')


def url_safe(string, separator='-'):
    """Converts a string to a format that is suitable for pretty urls.

    Args:
        separator (string): The separator to use for replaced characters
    """
    string = unicodedata.normalize('NFKD', string)\
                        .encode('ascii', 'ignore').decode('ascii')
    string = re.sub(r'(?i)[^a-z0-9\-_]+', separator, string)
    re_escaped = re.escape(separator)
    string = re.sub(r'{}{{2,}}'.format(re_escaped), separator, string)
    return string.strip(separator).lower()


def camelcase(string, uppercase=True):
    """Converts a string to camelCase.

    Args:
        uppercase (bool): Whether or not to capitalize the first character
    """
    if uppercase:
        return re.sub(r'(?:^|_)(.)', lambda s: s.group(1).upper(), string)
    else:
        return string[0].lower() + camelcase(string)[1:]


def snakecase(string):
    """Converts a string to snake_case.
    """
    string = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', string)
    string = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', string)
    return string.replace('-', '_').lower()


plurals = (
    (r'(?i)(ss)$', r'\1es'),
    (r'(?i)(s)$', r'\1'),
    (r'y$', r'ies'),
    (r'$', r's')
)


def pluralize(string):
    """Returns the plural of a string.
    """
    for pattern, replacement in plurals:
        if re.search(pattern, string):
            return re.sub(pattern, replacement, string)
    return string
