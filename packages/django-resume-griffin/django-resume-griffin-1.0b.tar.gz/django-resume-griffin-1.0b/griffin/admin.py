from django.contrib import admin
from . models import *
from griffin.forms import AttendanceForm

class AttendanceAdmin(admin.ModelAdmin):
    form = AttendanceForm

class PositionAdmin(AttendanceAdmin):
    pass

my_models = (
    (attendance.Position, PositionAdmin),
    (attendance.Attendance, AttendanceAdmin),
    attendance.Student,
    attendance.CollegeStudent,
    attendance.UniversityStudent,
    
    contactfield.EmailFieldModel,
    contactfield.PhoneFieldModel,
    contactfield.WebPageFieldModel,
    contactfield.OtherContactFieldModel,
    
    entity.CorporateEntity,
    entity.Person,
    entity.Applicant,
    entity.Company,
    entity.School,
    entity.Project,
    
    resume.Resume,
    
    skill.Skill,
)

for m in my_models:
    if isinstance(m, list) or isinstance(m, tuple):
        admin.site.register(*m)
    else:
        admin.site.register(m)
