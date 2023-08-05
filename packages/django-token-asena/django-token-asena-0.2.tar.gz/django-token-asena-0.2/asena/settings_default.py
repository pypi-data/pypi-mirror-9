import string
from django.utils.translation import ugettext_lazy as _

"""
" Default django settings for Token Asena
" NOTE: Remember to append _DEFAULT.
"""

ASENA_CHAR_SET_DEFAULT=str(string.ascii_letters + string.digits)

""" For security you can allow or forbid certain messages to be shown.
"""
ASENA_SECURITY_CONFIG_DEFAULT = {
    'show_timeout_error' : True,
    'show_expired_error' : True,
    'show_disabled_error' : True,
    'show_invalid_error' : True,
}

ASENA_ERROR_MESSAGES_DEFAULT = {
    'general' : _("Sorry; you are not authorized to view this page."),
    'timeout' : _("Your session has expired."),
    'expired' : _("The token is no longer valid."),
    'disabled' : _("That token has been disabled."),
    'invalid' : _("The token is not valid."),
}

"""
" The name for the session cookie.
"""
ASENA_SESSION_NAME_DEFAULT='asena_token_value'

"""
" The name of the session timeout cookie.
"""
ASENA_SESSION_TIMEOUT_NAME_DEFAULT='asena_token_timeout'

"""
" The date format for converting to and from a date.
" :see: datetime.datetime.strptime
"""
ASENA_DATETIME_FORMAT_DEFAULT="%c"

"""
" The name of the GET or POST key.
"""
ASENA_URL_KEY_DEFAULT='token'

"""
" A regexp for how to split a "session timeout." For example, if the
" ASENA_TIMEOUT_SEPARATORS value is r'[hms]', the value '0h4m2s' will be
" parsed as datetime.timedelta(0, 4, 2)
"""
ASENA_TIMEOUT_SEPARATORS_DEFAULT=r'[\,\:]'
