from django.conf.urls import patterns, url, include

from ..views import notice_settings


urlpatterns = patterns(
    "",
    url(r"^account/", include("account.urls")),
    url(r"^settings/$", notice_settings, name="notification_notice_settings"),
)
