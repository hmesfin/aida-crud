from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class AidaBaseModel(models.Model):
    """Base model with common fields for all AIDA-CRUD models"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        editable=False,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        editable=False,
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        """Override save to handle user tracking"""
        if hasattr(self, "_current_user"):
            if not self.pk:
                self.created_by = self._current_user
            self.updated_by = self._current_user
        super().save(*args, **kwargs)

    @classmethod
    def get_field_metadata(cls):
        """Returns metadata about model fields for frontend auto-configuration"""
        metadata = {}
        for field in cls._meta.fields:
            field_info = {
                "name": field.name,
                "type": field.__class__.__name__,
                "required": not field.blank and not field.null,
                "editable": field.editable,
                "help_text": field.help_text,
                "verbose_name": field.verbose_name,
            }

            if hasattr(field, "choices") and field.choices:
                field_info["choices"] = [{"value": k, "label": v} for k, v in field.choices]

            if hasattr(field, "max_length"):
                field_info["max_length"] = field.max_length

            metadata[field.name] = field_info

        return metadata


class SoftDeleteModel(AidaBaseModel):
    """Model with soft delete functionality"""

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted",
        editable=False,
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard=False):
        """Soft delete by default, hard delete if specified"""
        if hard:
            super().delete(using=using, keep_parents=keep_parents)
        else:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            if hasattr(self, "_current_user"):
                self.deleted_by = self._current_user
            self.save()

    def restore(self):
        """Restore a soft-deleted object"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()
