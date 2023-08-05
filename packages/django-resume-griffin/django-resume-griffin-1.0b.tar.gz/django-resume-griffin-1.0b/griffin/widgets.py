from django.db import models
from datetime import date
from django import forms
from django.core.validators import RegexValidator

import os, calendar, re, datetime

import logging
logger = logging.getLogger('to_terminal')


# Set up the calendar data necesary for the widget.

months = calendar.month_name[:]
MONTH_CHOICES = [(str(i), months[i]) for i in range(1, len(months))]
logger.debug("Month choices: %s"%(MONTH_CHOICES,))
MAX_YEAR = datetime.date.today().year+1
MIN_YEAR = MAX_YEAR-100
YEAR_CHOICES = [(str(i), str(i)) for i in range(MIN_YEAR, MAX_YEAR)]
YEAR_CHOICES.reverse()

SPLIT_CHAR='/'

class FuzzyDateWidget(forms.MultiWidget):

    def __init__(self, attrs):
        month_choices=MONTH_CHOICES
        year_choices=YEAR_CHOICES
        if not attrs.pop('required', False):
            logger.debug("Field is not required.")
            month_choices = [['', '',], ] + month_choices
            year_choices = [['', ''], ] + year_choices
        widgets = (
            forms.Select(choices=month_choices),
            forms.Select(choices=year_choices),
        )
        super(FuzzyDateWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if not value:
            return [None, None]
        return [value.month, value.year]
