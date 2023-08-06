# validation.py

r'''Column-level validation functions.

 * :func:`validate_min`
 * :func:`validate_max`
 * :func:`strip_value`
 * :func:`rstrip_value`
 * :func:`validate_min_length`
 * :func:`validate_max_length`
 * :func:`validate_phone_strict`
 * :func:`validate_phone`
 * :func:`validate_email`
 * :func:`no_html_chars`
 * :func:`must_not_match`
'''

import re


__all__ = ('validate_min', 'validate_max', 'validate_min_length',
           'validate_max_length', 'strip_value', 'rstrip_value',
           'validate_phone_strict', 'validate_phone', 'validate_email',
           'no_html_chars', 'must_not_match',
          )


def validate_min(min):
    r'''Ensures that the value is at least min.

        >>> validate_min(1)(None, 0)
        (0, 'Must be at least 1')
        >>> validate_min(1)(None, 1)
        (1, None)
        >>> validate_min(1)(None, 2)
        (2, None)
    '''
    def validate_min(key, value):
        if value is None: return None, None
        if value < min:
            return value, validate_min.info[2].format(min=min)
        return value, None
    validate_min.info = ('min', min, "Must be at least {min}")
    return validate_min

def validate_max(max):
    r'''Ensures that the value is at least max.

        >>> validate_max(1)(None, 1)
        (1, None)
        >>> validate_max(1)(None, 2)
        (2, 'Must be no more than 1')
    '''
    def validate_max(key, value):
        if value is None: return None, None
        if value > max:
            return value, validate_max.info[2].format(max=max)
        return value, None
    validate_max.info = ('max', max, "Must be no more than {max}")
    return validate_max

def strip_value(key, value):
    r'''Strips whitespace off of the beginning and end of the user value.
    '''
    if value is None: return None, None
    return value.strip(), None
strip_value.info = None

def rstrip_value(key, value):
    r'''Strips whitespace off of the end of the user value.
    '''
    if value is None: return None, None
    return value.rstrip(), None
rstrip_value.info = None

def validate_min_length(min_length):
    r'''Ensures that the value is at least min_length.

        >>> validate_min_length(1)(None, '')
        ('', 'Requires minimum of 1 character')
        >>> validate_min_length(2)(None, '')
        ('', 'Requires minimum of 2 characters')
        >>> validate_min_length(1)(None, '1')
        ('1', None)
        >>> validate_min_length(1)(None, '12')
        ('12', None)
    '''
    def validate_min_length(key, value):
        if value is None: return None, None
        if len(value) < min_length:
            return (value,
                    validate_min_length.info[2].format(min_length=min_length))
        return value, None
    validate_min_length.info = ('min_length', min_length,
                                "Requires minimum of {{min_length}} character{}"
                                  .format('' if min_length == 1 else 's'))
    return validate_min_length


def validate_max_length(max_length):
    r'''Ensures that the value is no longer than max_length.

        >>> validate_max_length(5)(None, '12345')
        ('12345', None)
        >>> validate_max_length(5)(None, '')
        ('', None)
        >>> validate_max_length(5)(None, '123456')
        ('123456', 'Exceeds maximum length of 5 characters')
    '''
    def validate_max_length(key, value):
        if value is None: return None, None
        if len(value) > max_length:
            return (value,
                    validate_max_length.info[2].format(max_length=max_length))
        return value, None
    validate_max_length.info = ('max_length', max_length,
                                "Exceeds maximum length of {{max_length}} "
                                "character{}"
                                  .format('' if max_length == 1 else 's'))
    return validate_max_length


strict_phone_regex = re.compile(r'(\([0-9]{3}\)|[0-9]{3})'
                                r'[ -]?([0-9]{3})'
                                r'[ -]?([0-9]{4})$')
def validate_phone_strict(key, value, regex=strict_phone_regex):
    r'''Validates a phone number, not allowing any information after the
    number.

        >>> validate_phone_strict(None, '(123)456-7890')
        ('123-456-7890', None)
        >>> validate_phone_strict(None, '123 456 7890 ')
        ('123-456-7890', None)
        >>> validate_phone_strict(None, '1234567890')
        ('123-456-7890', None)
        >>> validate_phone_strict(None, '123456789')
        ('123456789', 'Invalid phone number')
    '''
    if value is None: return None, None
    value = value.strip()
    match = regex.match(value)
    if match is None:
        return value, validate_phone_strict.info[2]
    area_code = match.group(1)
    if len(area_code) == 5:
        area_code = area_code[1:4]
    value = "{}-{}-{}".format(area_code, match.group(2), match.group(3))
    if match.lastindex == 4:
        value += " " + match.group(4).strip()
    return value, None
validate_phone_strict.info = ('must_match_regex', strict_phone_regex.pattern,
                              "Invalid phone number")


phone_regex = re.compile(strict_phone_regex.pattern[:-1] +
                         r'( +[a-zA-Z0-9.() -]+)? *$')
def validate_phone(key, value):
    r'''Validates a phone number.

    Allows any additional text after the phone number (such as extensions).

        >>> validate_phone(None, '(123)456-7890  ext. 44 ask for Bill ')
        ('123-456-7890 ext. 44 ask for Bill', None)
        >>> validate_phone(None, '123 456 7890 ')
        ('123-456-7890', None)
        >>> validate_phone(None, '1234567890')
        ('123-456-7890', None)
        >>> validate_phone(None, '123456789')
        ('123456789', 'Invalid phone number')
    '''
    return validate_phone_strict(key, value, phone_regex)
validate_phone.info = ('must_match_regex', phone_regex.pattern,
                       "Invalid phone number")


email_regex = re.compile(
  r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
  r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
  r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)
def validate_email(key, value):
    r'''Validate email address.

        >>> validate_email(None, 'bob@gmail')
        ('bob@gmail', None)
        >>> validate_email(None, 'john smith@hotmail.com')
        ('john smith@hotmail.com', 'Invalid email address')
        >>> validate_email(None, 'john.smith-4@hotmail.com')
        ('john.smith-4@hotmail.com', None)
    '''
    if value is None: return None, None
    match = email_regex.match(value)
    if match is None:
        return value, validate_email.info[2]
    return value, None
validate_email.info = ('must_match_regex', email_regex.pattern,
                       "Invalid email address")


# FIX: Add other unicode variants of < >
no_html_regex = re.compile(r'[<>]')
def no_html_chars(key, value):
    r'''Ensures that the value has no tag delimiters.

        >>> no_html_chars(None, "how's <this?")
        ("how's <this?", "Illegal character: '<'")
        >>> no_html_chars(None, "or this>?")
        ('or this>?', "Illegal character: '>'")
        >>> no_html_chars(None, "or -- maybe, 'this'?!...")
        ("or -- maybe, 'this'?!...", None)
    '''
    if value is None: return None, None
    match = no_html_regex.search(value)
    if match is not None:
        return value, no_html_chars.info[2].format(match=match.group(0))
    return value, None
no_html_chars.info = ('must_not_include_regex', no_html_regex.pattern,
                      "Illegal character: '{match}'")


def must_not_match(regex, message):
    r'''Ensures that the value does not match the regex.

        >>> must_not_match(r'[a-z]*$', 'ouch')(None, "how's <this?")
        ("how's <this?", None)
        >>> must_not_match(r'[a-z]*$', 'ouch')(None, "bogus")
        ('bogus', 'ouch')
    '''
    c_regex = re.compile(regex)
    def check_regex(key, value):
        if value is None: return None, None
        if c_regex.match(value) is not None:
            return value, message
        return value, None
    check_regex.info = ('must_not_match_regex', regex, message)
    return check_regex

