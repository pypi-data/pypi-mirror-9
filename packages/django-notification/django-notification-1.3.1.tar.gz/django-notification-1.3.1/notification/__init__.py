import pkg_resources


__version__ = pkg_resources.get_distribution("django-notification").version

default_app_config = "notification.apps.AppConfig"
