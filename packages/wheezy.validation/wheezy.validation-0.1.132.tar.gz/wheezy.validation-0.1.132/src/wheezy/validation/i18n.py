
""" ``i18n`` module.
"""


def thousands_separator(gettext):
    # thousands separator
    return gettext(',')


def decimal_separator(gettext):
    # decimal point separator
    return gettext('.')


def default_date_input_format(gettext):
    # default date input format: 2008/5/18.
    return gettext('%Y/%m/%d')


def fallback_date_input_formats(gettext):
    # fallback date input formats: 5/18/2008.
    # Use | to separate multiple values.
    return gettext('%m/%d/%Y|%Y-%m-%d|%m/%d/%y')


def default_time_input_format(gettext):
    # default time input format: 16:34.
    return gettext('%H:%M')


def fallback_time_input_formats(gettext):
    # fallback time input formats: 16:34:52.
    # Use | to separate multiple values.
    return gettext('%H:%M:%S')


def default_datetime_input_format(gettext):
    # default datetime input format: 2008/5/18 16:34
    return gettext('%Y/%m/%d %H:%M')


def fallback_datetime_input_formats(gettext):
    # fallback datetime input formats: 2008/5/18 16:34:52.
    # Use | to separate.
    return gettext('%Y/%m/%d %H:%M:%S|%m/%d/%Y %H:%M|%m/%d/%Y %H:%M:%S|'
                   '%Y-%m-%d %H:%M|%Y-%m-%d %H:%M:%S|%m/%d/%y %H:%M|'
                   '%m/%d/%y %H:%M:%S')
