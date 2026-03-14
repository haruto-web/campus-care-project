from django.db import models
from django.conf import settings


class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

    def unread_count_for(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField(blank=True)
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def is_image(self):
        if self.attachment:
            return self.attachment.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
        return False


class MessageReport(models.Model):
    REASON_CHOICES = [
        ('harassment', 'Harassment / Bullying'),
        ('inappropriate', 'Inappropriate Content'),
        ('threat', 'Threat / Violence'),
        ('hate_speech', 'Hate Speech'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    CONSEQUENCE_CHOICES = [
        ('warning', 'Issue Warning'),
        ('suspend', 'Suspend Messaging'),
        ('refer', 'Refer to Admin'),
        ('no_action', 'No Action Needed'),
    ]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='filed_reports')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    consequence = models.CharField(max_length=20, choices=CONSEQUENCE_CHOICES, blank=True)
    counselor_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resolved_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.reporter} on msg#{self.message_id} [{self.status}]"

    @property
    def reported_user(self):
        return self.message.sender
