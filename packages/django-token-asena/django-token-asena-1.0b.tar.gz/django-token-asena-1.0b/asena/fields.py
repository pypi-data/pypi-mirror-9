from django import forms
from asena.widgets import *

from django.conf import settings
import logging, pprint, os
logger = logging.getLogger('to_terminal')

class TokenField(forms.MultiValueField):
    #widget = TokenWidget
    
    def __init__(self, *args, **kwargs):
        token_value = kwargs.pop('token_value', None)
        self.widget = TokenWidget(attrs={'token_value' : token_value})
        fields = (forms.CharField(), forms.IntegerField())
        super(TokenField, self).__init__(fields, *args, **kwargs)
    
    def compress(self, data_list):
        logger.debug("Compressing data list %s"%pprint.pformat(data_list))
        if len(data_list) >= 1:
            return data_list[0]
        return None
    
class TokenSetField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        self.widget = TokenSetWidget()
        fields = (
            forms.MultipleChoiceField(),
        )
        super(TokenSetField, self).__init__(fields, *args, **kwargs)
        
    def compress(self, data_list):
        logger.debug("Compressing data list %s"%pprint.pformat(data_list))
        if len(data_list) > 0:
            return data_list.join(',')
        return ''

class TimeDeltaField(forms.MultiValueField):
        
    fields = (
        forms.IntegerField(label="Hours", min_value=0, max_value=100),
        forms.IntegerField(label="Minutes", min_value=0, max_value=60),
    )
    
    widget=TimeDeltaWidget
    
    def clean(self, value):
        #v = super(TimeDeltaField, self).clean(value)
        #logger.debug("Cleaning %s -> %s"%(value, v))
        return self.compress(value)

    def compress(self, data_list):
        """ Compress the TimeDeltaField. If any fields are left blank,
        fill them in with a zero.
        """
        dl = data_list + [0,]*(2 - len(data_list or []))
        data = ','.join([str(d or '0') for d in dl])
        logger.debug("Compressing %s -> %s."%(data_list, data))
        return data
