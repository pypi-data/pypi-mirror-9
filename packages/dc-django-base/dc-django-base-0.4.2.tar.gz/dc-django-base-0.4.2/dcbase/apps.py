from django.apps import AppConfig


TIMEZONE_SESSION_KEY = '_timezone'


class DcBaseApp(AppConfig):
    name = 'dcbase'
    label = 'dcbase'
    verbose_name = 'DC Base'
