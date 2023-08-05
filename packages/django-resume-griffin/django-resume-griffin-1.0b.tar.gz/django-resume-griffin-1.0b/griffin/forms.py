from django.forms import ModelForm
from griffin.models import *

from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from griffin.fields import FuzzyDateInput
from griffin.models.attendance import Attendance

class AttendanceForm(ModelForm):
    date_begin = FuzzyDateInput()
    date_end = FuzzyDateInput(required=False,
            help_text=_("Leave blank if you still work here."))

    class Meta:
        model=Attendance
