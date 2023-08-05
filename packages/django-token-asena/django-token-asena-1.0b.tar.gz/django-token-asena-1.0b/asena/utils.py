import random
from datetime import datetime, timedelta

from django.conf import settings

from asena import settings_default

import logging
logger = logging.getLogger('to_terminal')
import pprint

def random_chars(char_set, length):
    """ Choose random characters from a set.
    
    :param char_set: The character set.
    :type char_set: str
    
    :param length: the length of the set.
    :type length: int
    
    :return: A string of random characters chosen from char_set.
    """
    s = ""
    sz = len(char_set)-1
    r = random.SystemRandom()
    for i in range(0, length):
        n = r.randint(0, sz)
        s = s + char_set[n]
    return s

def random_chars_set(char_set, length, count):
    out_set = []
    for i in range(0, count):
        out_set.append(random_chars(char_set, length))
    return out_set

def html_attrs(attrs):
    """ Convert the attrs in dict format to an HTML format.
    
    :param attrs: The attributes for the element
    :type attrs: dict
    
    :return: string representing the attributes portion of a tag.
    """
    html = ""
    for a in attrs.items():
        if a[1]:
            html = html + "%s=\"%s\" "%(a)
    return html

def get_setting(setting, alt_value):
    if hasattr(settings, setting):
        return settings.setting
    return alt_value

def get_default_setting(setting):
    default_setting_key='%s_DEFAULT'%setting
    if hasattr(settings, setting):
        return settings.setting
    elif hasattr(settings_default, default_setting_key):
        return getattr(settings_default, default_setting_key)
    else:
        raise AttributeError("Missing default value ''%s``"%default_setting_key)

def make_url(base, **kwargs):
    sep = '?'
    logger.debug("Making URL with %s and %s"%(base, pprint.pformat(kwargs)))
    for k,v in kwargs.items():
        base = str(base + sep + k + '=' + v)
        if sep == '?':
            sep = '&'
    return base

def get_session_time_remaining(session_data, _date=datetime.now()):
    """ Calculate the amount of time remaining for the session as a
    datetime.timedelta object. 

    :param session_data: The client's session.
    :type session_data: backends.base.SessionBase

    :param _date: The initial date to test. Default is datetime.datetime.now()
                  Mainly used for testing.
    :default _date: datetime.datetime.now()
    :type _date: datetime.datetime

    :return: The amount of time remaining as a timedelta object.

    """
    timeout_name = get_default_setting('ASENA_SESSION_TIMEOUT_NAME')
    session_name = get_default_setting('ASENA_SESSION_NAME')
    dt_format = get_default_setting('ASENA_DATETIME_FORMAT')

    # Assume that if the session data does not exist, it has expired.
    if not session_data:
        return None

    exp_date = session_data.get(timeout_name, None)

    if not exp_date:
        return None

    exp_date = datetime.strptime(exp_date, dt_format)

    logger.debug("It is now %s. The session wil end at %s"%(
        _date, exp_date))

    diff = exp_date - _date

    # We can think of timedelta() as the int value ``0``. This tests if there
    # is a negative difference in time.
    if diff <= timedelta():
        return timedelta()

    # Otherwise, just return the difference.
    return diff

def has_session_expired(session_data, _date=datetime.now()):
    """ True if the token session has expired.
       :return: True if the session has expired, False otherwise.
    """
    remain = get_session_time_remaining(session_data, _date)
    if remain:
        return not (remain > timedelta())
    return True
