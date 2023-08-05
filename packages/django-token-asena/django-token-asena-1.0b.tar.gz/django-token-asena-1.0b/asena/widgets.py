import re

from django import forms
from django.utils.text import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.templatetags.static import static
from django.conf import settings

from asena.utils import html_attrs

import logging, pprint, os
logger = logging.getLogger('to_terminal')

""" Constant to pass in to the "onClick" HTML attribute for a button
"""
ONCLICK_BUTTON_METHOD="generateAsenaTokens('%(id)s'); return false;"

""" In case the static URL changes, make it a constant, too
"""
STATIC_JS='tokenGeneration.js'

class Button(forms.Widget):
    def __init__(self, attrs):
        self.attrs = attrs
        self.label = self.attrs.pop('label', '')
        self.on_click_method = attrs.pop('onClick', None)
        
    def render(self, name, value, attrs=None):
        """ Render the button.
        
        If given an ``onClick`` attribute, id of the widget will be passed in to
        the function parameters.
        
        :param name: The name of the widget
        :type name: str
        
        :param value: The value of the widget (unused).
        :type value: void
        
        :param attrs: Attributes for the widget.
        :type attrs: dict
        """
        if 'id' in attrs and self.on_click_method:
            attrs.update({
                'onClick' : str(self.on_click_method%{'id' : attrs['id'],}),
                'type' : 'button',
            })
            
        # It's ugly, but first we need to prepend some javascript.
        js = static(STATIC_JS)
        
        s = """<script type="text/javascript"></script>
<script type="text/javascript" src="%s"></script>"""%js
        
        return mark_safe(s + "<button %s>%s</button>"%(html_attrs(attrs),
                                                   self.label))
    
class SizeWidget(forms.NumberInput):
    def render(self, name, value, attrs):
        html = super(SizeWidget, self).render(name, value, attrs)
        return mark_safe('<label for="%s">Size:</label>%s'%(name, html))

class TokenWidget(forms.MultiWidget):
    
    def __init__(self, attrs={}):
        """ A widget to generate a token.
        
        :param attrs:   attributes for the widget. So far attrs is largely
                        ignored except for the key ``token_value`` wich is the 
                        value of the token we want to generate.
        
        :type attrs:    dict
        """
        logger.debug("Token attributes: %s"%pprint.pformat(attrs))
        token_value = attrs.pop('token_value', None)
        text_attrs = {'disabled' : '1',}
        if token_value:
            text_attrs.update({'value' : token_value,})
        widgets = [forms.TextInput(text_attrs),
                   SizeWidget(),
                   Button(attrs={'onClick' : ONCLICK_BUTTON_METHOD,}),
               ]
        super(TokenWidget, self).__init__(widgets, attrs)
    
    def decompress(self, value):
        if not value:
            return [None,]
        logger.debug("Decompressing value \"%s\""%value)
        return [value,]
    
class TokenSetWidget(forms.MultiWidget):
    def __init__(self, attrs={}):
        button_attrs = {
            'label' : 'Generate',
            'onClick' : ONCLICK_BUTTON_METHOD,
        }
        widgets = (
            forms.SelectMultiple(),
            Button(button_attrs),
        )
        super(TokenSetWidget, self).__init__(widgets, attrs)
    
    def decompress(self, value):
        if not value:
            return [None,]
        logger.debug("Decompressing value \"%s\""%value)
        return [value,]

class TimeDeltaWidget(forms.MultiWidget):
    
    def __init__(self, attrs=None):
        
        default_style = 'width: 75px; float: left;'
        default_min = 0
        
        hours = forms.NumberInput({
            'style' : default_style,
            'min' : default_min,
            'max' : 100,
            'label' : 'Hours',
        })
        
        minutes = forms.NumberInput({
            'style' : default_style,
            'min' : default_min,
            'max' : 60,
            'label' : 'Minutes',
        })
        
        widgets = (hours, minutes)
        
        super(TimeDeltaWidget, self).__init__(widgets=widgets, attrs=attrs)
        
    def _get_attr_from_rendered_widget(self, attr, rendered_widget):
        """ Get an attribute from a rendered widget.
        
        :param attr: the attribute to extract.
        :type attr: string
        
        :param rendered_widget: The widget that's already been rendered.
        :type attr: unicode
        """
        attr_re = r'.+%(attr)s\=[\'"](?P<%(attr)s>[^"\']+)[\'"].+'%(
            {'attr' : attr})
        matches = re.match(attr_re, rendered_widget)
        if matches:
            return matches.group(attr)
        return None
    
    def _get_name_from_rendered_widget(self, rendered_widget):
        """ Get the ``name`` attribute value.
        
        :param rendered_widget: The widget that's already been rendered.
        :type attr: unicode
        
        :return: the name attribute value.
        """
        return self._get_attr_from_rendered_widget('name', rendered_widget)
    
    def _get_label_from_rendered_widget(self, rendered_widget):
        """ Get the ``label`` attribute value.
        
        :param rendered_widget: The widget that's already been rendered.
        :type attr: unicode
        
        :return: the label attribute value.
        """
        return self._get_attr_from_rendered_widget('label', rendered_widget)
        
    def format_output(self, rendered_widgets):
        """ Return the HTML for this multiwidget
        
        :see: forms.MultiWidget.format_output
        """
        s = u''
        
        label_style="padding: 5px 5px; margin: 0px 0px; " + \
            "display: inline-block; " + \
            "width: auto;";
        
        """ Here's what's tricky: we already have 'label' and 'name' attributes
        stored in the widget. But we're passed already-renderd widgets. So,
        for every widget we need to extract out the 'label' and 'name' 
        attributes from the rendered widgets. Ugly hack, but it works.
        """
        for i in range(0, len(rendered_widgets)):
            rw = rendered_widgets[i]
            name = self._get_name_from_rendered_widget(rw)
            label_text = self._get_label_from_rendered_widget(rw) or ''
            s = s + u'<span style="display:inline-block;">' + \
                unicode(rendered_widgets[i]) + \
                u'<label style="%s" '%label_style + \
                u'for="%s">%s</label>'%(name, label_text) + \
                u'</span>'
            
        #return u''.join(rendered_widgets)
        return s

    def decompress(self, value):
        val2 = [None]*2
        if value:
            val2 = [int(v) for v in value.split(',')]
        logger.debug("Decompressing %s -> %s"%(value, pprint.pformat(val2)))
        return val2
