from django.apps import AppConfig


class ClinicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_types.clinic'
    label = 'clinic'
    verbose_name = 'Clinic Management'
