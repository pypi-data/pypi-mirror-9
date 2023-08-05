from django.db.models import QuerySet, Manager

import managers
class SkillQuerySet(QuerySet):
    def all_skills(self, resume):
        attendances = resume.attendances.all()
        skills = []
        for a in attendances:
            for s in attendances.skills:
                if skill not in skills:
                    skills.append(skill)
        return skills 

class SkillManager(Manager):
    def get_queryset(self):
        return SkillQuerySet(self.model, using=self._db)
    
    def all_skills(self):
        return self.get_queryset().all_skills()
    
class AttendanceQuerySet(QuerySet):
    def all_attendances(self, resume):
        from attendee import Attendance
        return Attendance.objects.filter(resume=resume)

class AttendanceManager(Manager):
    def get_queryset(self):
        return AttendanceQuerySet(self.model, using=self._db)
    
    def all(self):
        return self.get_queryset().all_attendances()
      
class ResumeManager(Manager):
    def get_queryset(self):
        return super(ResumeManager, self).get_queryset()
