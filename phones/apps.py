from django.apps import AppConfig


class PhonesConfig(AppConfig):
    name = 'phones'

    def ready(self):
        import phones.signals
