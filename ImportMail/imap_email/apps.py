from django.apps import AppConfig


class ImapEmailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'imap_email'

    def ready(self):
        import imap_email.signals  # Подключение сигналов
