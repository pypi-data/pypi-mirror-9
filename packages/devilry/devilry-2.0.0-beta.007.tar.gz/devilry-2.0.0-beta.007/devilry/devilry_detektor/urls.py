from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required


from .views import admin_assignmentassembly

urlpatterns = patterns(
    '',
    url(r'^admin/assignmentassembly/(?P<assignmentid>\d+)$',
        login_required(admin_assignmentassembly.AssignmentAssemblyView.as_view()),
        name='devilry_detektor_admin_assignmentassembly'),
    )
