from django.conf.urls import url
from .views import ImportResults

urlpatterns = [
    url(r'^(?P<project_id>[\d-]+)/import_results/$', ImportResults.as_view(), name='earmaster_import_results'),
]
