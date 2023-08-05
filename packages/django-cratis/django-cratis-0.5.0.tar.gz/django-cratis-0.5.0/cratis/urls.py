from django.conf.urls import patterns
from django.conf import settings


urlpatterns = patterns('',)

for feature in settings.FEATURES:
    feature.configure_urls(urlpatterns)

