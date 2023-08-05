from django.db import models

class SkillQuerySet(models.manager):
    def __init__(self, resume, *args, **kwargs):
        self.resume = resume
        super(SkillQuerySet, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return Skill.objects.get(resume__pk=self.resume.pk)
