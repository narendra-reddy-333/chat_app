# chat/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Message, UnreadMessage, TypingIndicator



@receiver(post_save, sender=TypingIndicator)
def handle_typing_indicator_update(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{instance.conversation.id}",
        {
            'type': 'typing_indicator_update',
            'user_id': instance.user.id,  # Include user ID for better identification
            'is_typing': instance.is_typing
        }
    )


@receiver(post_delete, sender=TypingIndicator)
def handle_typing_indicator_delete(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{instance.conversation.id}",
        {
            'type': 'typing_indicator_update',
            'user_id': instance.user.id,  # Include user ID
            'is_typing': False
        }
    )
