import numbers
import ast


def convert(string_value, to_type_str=None):
    """ convert string value to base type representation """
    string_value = string_value.strip()
    try:
        types = {'float': float, 'int': int, 'bool': bool}
        if to_type_str:
            to_type = types.get(to_type_str, str)
            try:
                return to_type(string_value)
            except ValueError:
                return to_type(0)  # return standard value
        return ast.literal_eval(string_value)
    except (ValueError, SyntaxError):
        return string_value


def get_unit_prefixed(value):
    """ return the adapted value and prefix """
    exp_praefixes = [
        (1e-15, 'f'),
        (1e-12, 'p'),
        (1e-9, 'n'),
        (1e-6, 'µ'),
        (1e-3, 'm'),
        (1, ''),
        (1e3, 'k'),
        (1e6, 'M'),
        (1e9, 'G'),
        (1e12, 'T'),
        (1e15, 'P')
    ]
    if isinstance(value, numbers.Number) and value not in [0, float('NaN'), float('inf'), float('-inf')]:
        for exp, praefix in exp_praefixes:
            if abs(value) < exp*1000:
                return value/exp, praefix
    return value, ''


def get_short_value_text(value, unit):
    """ return shortened value string with unit prefixes or exponents for small and big numbers """
    postfix = ''
    if unit:
        unit_prefix = ''
        if not unit[0] in 'abcdefghijklmnopqrstuvwxyzµ°':
            value, unit_prefix = get_unit_prefixed(value)
        postfix = ' %s%s' % (unit_prefix, unit)

    if isinstance(value, numbers.Number) and not isinstance(value, bool):
        if isinstance( value, int ):
            value = '%g' % value
        else:
            value = '%.2f' % value

    return '%s%s' % (value, postfix)