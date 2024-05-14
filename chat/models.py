from datetime import timedelta
from django.db import models
from django.db.models import OuterRef
from django.utils import timezone

from groups.models import Group
from users.models import User


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    is_group = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)

    def __str__(self):
        if self.is_group:
            return f"Group: {self.group.name}"
        else:
            return f"Conversation between {self.participants.all()}"


class Message(models.Model):
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    @property
    def can_be_edited(self):
        """Checks if the message can be edited (within 5 minutes of creation)."""
        time_passed = timezone.now() - self.timestamp
        return time_passed < timedelta(minutes=5)


class TypingIndicator(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE)
    is_typing = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'conversation')

    def __str__(self):
        return f"{self.user}: {self.conversation}"


class UnreadMessage(models.Model):
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='unread_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('conversation', 'user')

    def __str__(self):
        return f"{self.conversation}: {self.count}"
