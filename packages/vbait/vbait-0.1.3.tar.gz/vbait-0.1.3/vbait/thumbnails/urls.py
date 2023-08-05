from django.conf.urls import patterns, include, url
from views import generate_image


urlpatterns = patterns('',
    url(r'^storeimages/(?P<path>.*)$', generate_image, name="generate_image"),
)