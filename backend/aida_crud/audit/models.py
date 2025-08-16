from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json

User = get_user_model()


class AuditLog(models.Model):
    """Model for tracking all CRUD operations"""

    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("RESTORE", "Restore"),
        ("BULK_CREATE", "Bulk Create"),
        ("BULK_UPDATE", "Bulk Update"),
        ("BULK_DELETE", "Bulk Delete"),
        ("EXPORT", "Export"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["action", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.object_repr} - {self.timestamp}"

    @classmethod
    def log_action(cls, user, action, obj=None, changes=None, request=None):
        """Create an audit log entry"""
        log_entry = cls(
            user=user, action=action, object_repr=str(obj) if obj else "", changes=changes or {}
        )

        if obj:
            log_entry.content_type = ContentType.objects.get_for_model(obj)
            log_entry.object_id = str(obj.pk)

        if request:
            log_entry.ip_address = cls.get_client_ip(request)
            log_entry.user_agent = request.META.get("HTTP_USER_AGENT", "")
            log_entry.request_method = request.method
            log_entry.request_path = request.path

        log_entry.save()
        return log_entry

    @staticmethod
    def get_client_ip(request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @classmethod
    def get_object_history(cls, obj):
        """Get all audit logs for a specific object"""
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.filter(content_type=content_type, object_id=str(obj.pk))

    @classmethod
    def get_user_activity(cls, user, limit=100):
        """Get recent activity for a user"""
        return cls.objects.filter(user=user)[:limit]
