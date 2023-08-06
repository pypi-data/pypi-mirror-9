from django.conf.urls import *
from django.conf import settings
from views.acl_bind import  ServiceBind

urlpatterns = patterns('dbaas_aclapi.views',
    url(r'^resources/(?P<database_id>\w+)$', ServiceBind.as_view()),
)
