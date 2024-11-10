import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Email


@receiver(post_save, sender=Email)
def notify_clients(sender, instance, **kwargs):
    """Отправка уведомлений всем подключенным клиентам при изменении данных."""
    channel_layer = get_channel_layer()
    users = Email.objects.all().values()
    user_list = list(users)
    user_list = user_list[::-1]
    async_to_sync(channel_layer.group_send)(
        "updates",  # Название группы
        {
            "type": "send_update",
            "text_data": json.dumps({'user': user_list}),
        },
    )
