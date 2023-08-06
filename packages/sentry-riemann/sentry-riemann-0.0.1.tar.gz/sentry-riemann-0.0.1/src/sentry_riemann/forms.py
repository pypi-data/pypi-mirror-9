# coding: utf-8
"""
sentry_statsd.forms
"""
from django import forms


class RiemannOptionsForm(forms.Form):
    host = forms.CharField(
        max_length=255,
        help_text='Riemann host (for example: "localhost")'
    )
    port = forms.IntegerField(
        max_value=65535,
        help_text='Riemann port (for example: "8125")'
    )
    prefix = forms.CharField(
        max_length=255,
        help_text='Prefix for Sentry metrics in Riemann (for example: "sentry")'
    )
    track_only_new = forms.BooleanField(
        required=False,
        help_text='Add statsd count to only new exceptions')
