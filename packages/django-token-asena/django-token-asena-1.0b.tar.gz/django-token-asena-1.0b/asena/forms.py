from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from asena.models import Token, TokenSet
from asena.widgets import TokenWidget
from asena.fields import TokenField, TokenSetField, TimeDeltaField

from asena.utils import (random_chars, random_chars_set, get_setting, 
    get_default_setting)

import logging, pprint
logger = logging.getLogger('to_terminal')

class TokenWall(forms.Form):
    token = forms.CharField(label="Token Text")
   
    def clean(self):
        cleaned_data = super(TokenWall, self).clean()

        logger.debug("Cleaning data: %s"%pprint.pformat(cleaned_data))
        
        token_value = None
        if 'token' in cleaned_data:
            token_value = cleaned_data['token']
        
        # Validate the data.
        asena_security = get_default_setting('ASENA_SECURITY_CONFIG')
        asena_errors = get_default_setting('ASENA_ERROR_MESSAGES')
        
        code = None
        
        t = None
        if token_value:
            t = Token.objects.get(value=token_value)
            
        if ((not t) or t.has_expired() or t.is_disabled()):
            code = 'general'
        
        if (not t) and asena_security['show_invalid_error']:
            code = 'invalid'
        
        elif t.has_expired() and asena_security['show_timeout_error']:
            code = 'expired'
                
        elif t.is_disabled() and asena_security['show_disabled_error']:
            code='disabled'
        
        if code:
            raise forms.ValidationError(asena_errors[code], code)
        
        logger.debug("Cleaned data: %s"%pprint.pformat(cleaned_data))

    def get_token(self):
        """ If the form is valid, return the token from the token value.
        """
        if not self.is_valid():
            logger.warn("TokenWall form data is not valid.")
            return None
    
        tt = self.cleaned_data['token']
        logger.debug("Looking for token '%s'"%tt)
        return Token.objects.get(value=tt)
        
    
class TokenCreationForm(forms.ModelForm):
    value = TokenField()
    comment = forms.CharField(widget=forms.Textarea)
    
    def clean(self):
        cleaned_data = super(TokenCreationForm, self).clean()
        return cleaned_data
    
    class Meta:
        model = Token
        fields = ['value', 'comment']

class TokenSetCreationForm(forms.ModelForm):
    count = forms.IntegerField(label="Number of tokens", required=False,
        help_text="Leave blank to update a token set.")
    length = forms.IntegerField(label="Length of each token", required=False,
        help_text="Leave blank to udpate a token set.")
    session_timeout = TimeDeltaField(required=False,
            label="For how long will the session be valid?",
            help_text="Note that the session will automatically end " +
                "when the browser data is cleared.")
    
    def __init__(self, *args, **kwargs):
        logger.debug("Token Set:")
        logger.debug("args\t%s"%(pprint.pformat(args)))
        logger.debug("kwargs\t%s"%(pprint.pformat(kwargs)))
        super(TokenSetCreationForm, self).__init__(*args, **kwargs)
        #self.instance = kwargs.pop('instance', None)
        
    def clean(self, *args, **kwargs):
        cleaned_data = super(TokenSetCreationForm, self).clean(*args, **kwargs)
        self.cleaned_data = cleaned_data
        return cleaned_data
    
    def save(self, force_insert=False, force_update=False, commit=True):
        t = super(TokenSetCreationForm, self).save(commit=False)
        
        count = self.cleaned_data.pop('count', 0) or 0
        length = self.cleaned_data.pop('length', 0) or 0
        
        values = []
        
        logger.debug("Timeout: %s"%self.cleaned_data.get('session_timeout',
            None))
        
        if self.instance:
            ts = self.instance.get_tokens()
            count = count - len(ts)
            if count < 1: count = 0
            token_set = super(TokenSetCreationForm, self).save(commit=True)
            
        else:
            token_set = TokenSet.objects.create(**self.cleaned_data)
        
        if count > 0 and length > 0:
            values = random_chars_set(get_default_setting('ASENA_CHAR_SET'), 
                length, count)
            logger.debug("Generate tokens: %s"%pprint.pformat(values))
            
        for v in values:
            Token.objects.create(value=v, token_set=token_set)
        
        return token_set
    
    class Meta:
        model = TokenSet
        fields = ['name', 'disabled', 'session_timeout', 'expiration',
                  'count', 'length', ]
