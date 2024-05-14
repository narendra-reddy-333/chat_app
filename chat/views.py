from django.db import transaction
from django.db.models import OuterRef, Subquery, Q
from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from groups.models import Group
from users.models import User
from .models import Conversation, Message, UnreadMessage
from .permissions import IsConversationParticipant
from .serializers import (ConversationListSerializer, ConversationSerializer,
                          MessageSerializer, TypingIndicatorSerializer, UnreadMessageSerializer)


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        conversations = self.request.user.conversations.all().select_related('group').prefetch_related('participants')

        # Subquery to get the latest message for each conversation
        latest_message_subquery = Message.objects.filter(
            conversation=OuterRef('pk')
        ).order_by('-timestamp')[:1]

        # Annotate conversations with the latest message timestamp
        conversations = conversations.annotate(
            last_message_timestamp=Subquery(latest_message_subquery.values('timestamp')),
            last_message=Subquery(latest_message_subquery.values('content'))
        )

        # Order by annotated timestamp
        return conversations.order_by('-last_message_timestamp')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = (permissions.IsAuthenticated, IsConversationParticipant)
    queryset = Conversation.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MessageCreateView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, IsConversationParticipant)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        recipient_username = self.request.data.get('recipient_username')  # Assuming you send username in the request
        group_id = self.request.data.get('group_id')  # Assuming you send group_id if it's a group message
        if recipient_username:
            # One-on-one conversation
            recipient = get_object_or_404(User, username=recipient_username)

            conversation = Conversation.objects.filter(
                is_group=False,
                participants=self.request.user
            ).filter(
                participants=recipient
            ).first()  # Use .first() to get one or None

            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(self.request.user, recipient)
        elif group_id:
            # Group conversation
            group = get_object_or_404(Group, pk=group_id)
            conversation, created = Conversation.objects.get_or_create(
                is_group=True, group=group
            )
            conversation.participants.add(self.request.user)
        else:
            raise serializers.ValidationError("Either recipient_id or group_id is required.")

        message = Message.objects.create(conversation=conversation, sender=self.request.user,
                                         content=self.request.data.get('content'))
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageEditView(generics.RetrieveUpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Message.objects.all()

    def perform_update(self, serializer):
        instance = self.get_object()
        self.check_object_permissions(self.request, instance)
        serializer.save(edited=True)

    def check_object_permissions(self, request, obj):
        if request.user != obj.sender:
            raise PermissionDenied("You are not allowed to edit this message.")
        if not obj.can_be_edited:
            raise PermissionDenied("You cannot edit this message now.")


class TypingIndicatorUpdateView(generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = TypingIndicatorSerializer
    permission_classes = (permissions.IsAuthenticated, IsConversationParticipant)

    def perform_create(self, serializer):
        conversation = self.get_object()  # Assuming get_object retrieves the conversation
        serializer.save(user=self.request.user, conversation=conversation, is_typing=True)

    def perform_destroy(self, instance):
        instance.delete()


class MarkAsReadView(generics.UpdateAPIView):
    serializer_class = UnreadMessageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        conversation_id = self.kwargs['conversation_pk']
        unread, _ = UnreadMessage.objects.get_or_create(
            conversation_id=conversation_id,
            user=self.request.user
        )
        return unread

    def perform_update(self, serializer):
        serializer.save(count=0)
