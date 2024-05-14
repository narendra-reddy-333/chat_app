import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, **kwargs)
        self.conversation_group_name = None
        self.user = None
        self.conversation_id = None
        print("hiiii")

    async def connect(self):

        self.user = self.scope['user']
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_pk']
        self.conversation_group_name = f'chat_{self.conversation_id}'

        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        await self.accept()

        unread_count = await self._get_unread_count()
        if unread_count:
            await self.send_json({
                'type': 'unread_count',
                'conversation_id': self.conversation_id,
                'unread_count': unread_count
            })

    async def disconnect(self, close_code):
        if self.conversation_group_name:
            conversation = await self._get_conversation()
            if conversation:
                await self._update_typing_indicator(False, conversation)
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        handler_mapping = {
            'chat_message': self._handle_chat_message,
            'typing': self._handle_typing_indicator,
            'read_messages': self._handle_read_messages
        }
        handler = handler_mapping.get(message_type)
        if handler:
            await handler(content)

    async def _handle_chat_message(self, data):
        message = data['message']
        conversation = await self._get_conversation()
        if conversation:
            new_message = await self._create_message(message, conversation)
            await self._send_chat_message(new_message)
            await self._update_unread_counts(conversation, new_message)

    async def _handle_typing_indicator(self, data):
        is_typing = data['is_typing']
        conversation = await self._get_conversation()
        if conversation:
            await self._update_typing_indicator(is_typing, conversation)
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': self.user.id,
                    'is_typing': is_typing
                }
            )

    async def _handle_read_messages(self, data):
        conversation = await self._get_conversation()
        if conversation:
            await self._mark_conversation_as_read(conversation)

    async def chat_message(self, event):
        await self.send_json(event)

    async def typing_indicator(self, event):
        await self.send_json(event)

    async def unread_count_update(self, event):
        if event.get('recipient_id') == self.user.id:
            await self.send_json({
                'type': 'unread_count',
                'conversation_id': event['conversation_id'],
                'unread_count': event['unread_count']
            })

    async def _send_chat_message(self, message):
        from chat.serializers import MessageSerializer
        serializer = MessageSerializer(message)
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': serializer.data
            }
        )

    @database_sync_to_async
    def _get_conversation(self):
        from chat.models import Conversation
        try:
            return Conversation.objects.get(pk=self.conversation_id)
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def _create_message(self, message, conversation):
        from chat.models import Message
        return Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=message
        )

    @database_sync_to_async
    def _update_typing_indicator(self, is_typing, conversation):
        from chat.models import TypingIndicator
        indicator, created = TypingIndicator.objects.get_or_create(
            user=self.user, conversation=conversation
        )
        indicator.is_typing = is_typing
        indicator.save()

    @database_sync_to_async
    def _update_unread_counts(self, conversation, message):
        recipients = conversation.participants.exclude(pk=message.sender.pk)
        for recipient in recipients:
            from chat.models import UnreadMessage
            unread_count, _ = UnreadMessage.objects.get_or_create(
                conversation=conversation, user=recipient
            )
            unread_count.count += 1
            unread_count.save()
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_group_name,
                {
                    'type': 'unread_count_update',
                    'conversation_id': conversation.id,
                    'unread_count': unread_count.count,
                    'recipient_id': recipient.id
                }
            )

    @database_sync_to_async
    def _get_unread_count(self):
        from chat.models import UnreadMessage
        try:
            unread_obj = UnreadMessage.objects.get(user=self.user, conversation_id=self.conversation_id)
            return unread_obj.count
        except UnreadMessage.DoesNotExist:
            return 0

    @database_sync_to_async
    def _mark_conversation_as_read(self, conversation):
        from chat.models import UnreadMessage
        unread_message, _ = UnreadMessage.objects.get_or_create(
            user=self.user, conversation=conversation
        )
        unread_message.count = 0
        unread_message.save()
        async_to_sync(self.channel_layer.group_send)(
            self.conversation_group_name,
            {
                'type': 'unread_count_update',
                'conversation_id': conversation.id,
                'unread_count': 0,
                'recipient_id': self.user.id
            }
        )
