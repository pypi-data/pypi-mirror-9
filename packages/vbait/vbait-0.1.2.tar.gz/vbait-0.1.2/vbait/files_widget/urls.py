from django.conf.urls import patterns, url
from views import upload, thumbnail_url

urlpatterns = patterns("",
    url(r'^upload/$', upload, name="files_widget_upload"),
    url(r'^thumbnail-url/$', thumbnail_url, name="files_widget_get_thumbnail_url"),
)
