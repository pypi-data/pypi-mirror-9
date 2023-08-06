from django.conf.urls import patterns, url

from .views import notice_settings


urlpatterns = patterns(
    "",
    url(r"^settings/$", notice_settings, name="notification_notice_settings"),
)
