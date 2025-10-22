from django.apps import AppConfig


class GymConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_types.gym'
    label = 'gym'
    verbose_name = 'Gym Management'
