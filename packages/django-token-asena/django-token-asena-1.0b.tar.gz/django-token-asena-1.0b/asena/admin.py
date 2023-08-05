from django.contrib import admin
from asena.models import *
from asena.forms import *

import logging
logger = logging.getLogger('to_terminal')

class TokenAdmin(admin.ModelAdmin):
    form = TokenCreationForm

class TokenSetAdmin(admin.ModelAdmin):
    form = TokenSetCreationForm

admin.site.register(TokenSet, TokenSetAdmin)
#admin.site.register(TokenSet)
logger.debug("Registered TokenSet")
admin.site.register(Token, TokenAdmin)
#admin.site.register(Token)
logger.debug("Registered Token")