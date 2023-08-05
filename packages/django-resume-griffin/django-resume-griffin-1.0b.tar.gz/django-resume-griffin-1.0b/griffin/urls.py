from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'griffin.views.index', name="index"),
    url(r'^griffin/(?P<applicant_id>\d+)$', 'griffin.views.resume.all', name='all_resumes'),
    url(r'^griffin/(?P<applicant_id>\d+)/(?P<resume_id>\d+)$', 'resume', name="resume"),
)
