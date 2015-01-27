# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django import forms
try:
    from django.forms.utils import flatatt
except ImportError:
    from django.forms.util import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html


class NamelessTextInput(forms.TextInput):
    """TextInput which does not render a ``name`` attribute."""

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))
        return format_html('<input{0} />', flatatt(final_attrs))
