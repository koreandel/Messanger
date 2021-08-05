from django.db import models
from apps.accounts.models import User


class Thread(models.Model):
    participants = models.ManyToManyField(
        User, blank=True, related_name="participant_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "thread"
        verbose_name_plural = "threads"

    def __str__(self):
        return f"{self.id}"


class Message(models.Model):
    class NewManager(models.Manager):
        def read(self):
            return super().get_queryset().filter(is_read=True)

        def unread(self):
            return super().get_queryset().filter(is_read=False)

    text = models.TextField()
    sender = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="sender_message",
    )
    thread = models.ForeignKey(
        Thread,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="thread_message",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    objects = NewManager()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "message"
        verbose_name_plural = "messages"

    def __str__(self):
        return f"{self.id}"
