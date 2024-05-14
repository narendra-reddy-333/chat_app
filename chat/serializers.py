from rest_framework import serializers
from .models import Conversation, Message, UnreadMessage, TypingIndicator


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username')
    can_be_edited = serializers.ReadOnlyField()

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'content', 'timestamp', 'edited', 'can_be_edited']
        read_only_fields = ['id', 'timestamp', 'can_be_edited', 'conversation', 'timestamp', 'sender', 'edited']


class ConversationListSerializer(serializers.ModelSerializer):
    other_entity_name = serializers.SerializerMethodField()
    other_entity_id = serializers.SerializerMethodField()
    last_message = serializers.CharField()
    unread_count = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'other_entity_name', 'other_entity_id', 'is_group', 'last_message', 'unread_count',
                  'participants']
        read_only_fields = ['id', 'last_message']

    def get_other_entity_name(self, obj):
        user = self.context['request'].user
        if obj.is_group:
            return obj.group.name
        else:
            return obj.participants.exclude(id=user.id).first().username

    def get_other_entity_id(self, obj):
        user = self.context['request'].user
        if obj.is_group:
            return obj.group.id
        else:
            return obj.participants.exclude(id=user.id).first().id

    def get_unread_count(self, obj):
        user = self.context['request'].user
        try:
            unread = UnreadMessage.objects.get(conversation=obj, user=user)
            return unread.count
        except UnreadMessage.DoesNotExist:
            return 0

    @staticmethod
    def get_participants(obj):
        return obj.participants.values_list('username', flat=True)


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'messages', 'unread_count']

    def get_unread_count(self, obj):
        user = self.context['request'].user
        try:
            unread = UnreadMessage.objects.get(conversation=obj, user=user)
            return unread.count
        except UnreadMessage.DoesNotExist:
            return 0


class TypingIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypingIndicator
        fields = ['id', 'user', 'conversation', 'is_typing']


class UnreadMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypingIndicator
        fields = ['id', 'user', 'conversation', 'is_typing']
