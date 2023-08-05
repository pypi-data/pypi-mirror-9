from django.db import models
from datetime import date
from django import forms
from django.core.validators import RegexValidator
from griffin.widgets import FuzzyDateWidget
from griffin.fuzzy_date import FuzzyDate

import os, calendar, re, datetime

import logging
logger = logging.getLogger('to_terminal')

months = calendar.month_name[:]
MONTH_CHOICES = [(str(i), months[i]) for i in range(1, len(months))]
logger.debug("Month choices: %s"%(MONTH_CHOICES,))
MAX_YEAR = datetime.date.today().year+1
MIN_YEAR = MAX_YEAR-100
YEAR_CHOICES = [(str(i), str(i)) for i in range(MIN_YEAR, MAX_YEAR)]
YEAR_CHOICES.reverse()

SPLIT_CHAR='-'

class FuzzyDateInput(forms.MultiValueField):
    fields = ()
    widget = None

    def __init__(self, *args, **kwargs):
        month_choices = MONTH_CHOICES
        year_choices = YEAR_CHOICES
        required=kwargs.get('required', False)
        if not required:
            month_choices = [['', ''], ] + month_choices
            year_choices = [['', ''], ] + year_choices
        kwargs.update({
            'fields' : (
                forms.ChoiceField(month_choices),
                forms.ChoiceField(year_choices),
            ),
            'widget' : FuzzyDateWidget(attrs={'required' : False,}),
        })
        super(FuzzyDateInput, self).__init__(*args, **kwargs)

    def compress(self, data_list):
        if not data_list or None in data_list:
            return None
        return FuzzyDate(*data_list)
