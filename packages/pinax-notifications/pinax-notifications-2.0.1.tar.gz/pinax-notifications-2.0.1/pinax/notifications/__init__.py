import pkg_resources


__version__ = pkg_resources.get_distribution("pinax-notifications").version

default_app_config = "pinax.notifications.apps.AppConfig"
