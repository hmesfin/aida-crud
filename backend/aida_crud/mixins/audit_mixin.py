from ..audit.models import AuditLog
from django.forms.models import model_to_dict


class AuditMixin:
    """Mixin to add audit logging to viewsets"""

    def perform_create(self, serializer):
        """Log create actions"""

        instance = serializer.save()

        if hasattr(self, "request"):
            AuditLog.log_action(
                user=self.request.user if self.request.user.is_authenticated else None,
                action="CREATE",
                obj=instance,
                changes={"created": model_to_dict(instance)},
                request=self.request,
            )

    def perform_update(self, serializer):
        """Log update actions"""
        old_instance = self.get_object()
        old_data = model_to_dict(old_instance)

        instance = serializer.save()
        new_data = model_to_dict(instance)

        changes = {
            "before": old_data,
            "after": new_data,
            "modified_fields": [
                field for field in new_data if old_data.get(field) != new_data.get(field)
            ],
        }

        if hasattr(self, "request"):
            AuditLog.log_action(
                user=self.request.user if self.request.user.is_authenticated else None,
                action="UPDATE",
                obj=instance,
                changes=changes,
                request=self.request,
            )

    def perform_destroy(self, instance):
        """Log delete actions"""
        deleted_data = model_to_dict(instance)

        if hasattr(self, "request"):
            AuditLog.log_action(
                user=self.request.user if self.request.user.is_authenticated else None,
                action="DELETE",
                obj=instance,
                changes={"deleted": deleted_data},
                request=self.request,
            )

        super().perform_destroy(instance)

    def perform_bulk_create(self, serializer):
        """Log bulk create actions"""
        instances = serializer.save()

        if hasattr(self, "request"):
            AuditLog.log_action(
                user=self.request.user if self.request.user.is_authenticated else None,
                action="BULK_CREATE",
                changes={
                    "created_count": len(instances),
                    "created_ids": [str(i.pk) for i in instances],
                },
                request=self.request,
            )

    def perform_bulk_update(self, serializer):
        """Log bulk update actions"""
        instances = serializer.save()

        if hasattr(self, "request"):
            AuditLog.log_action(
                user=self.request.user if self.request.user.is_authenticated else None,
                action="BULK_UPDATE",
                changes={
                    "updated_count": len(instances),
                    "updated_ids": [str(i.pk) for i in instances],
                },
                request=self.request,
            )

    def perform_bulk_destroy(self, queryset):
        """Log bulk delete actions"""
        ids = list(queryset.values_list("pk", flat=True))
        count = len(ids)

        if hasattr(self, "request"):
            AuditLog.log_action(
                user=self.request.user if self.request.user.is_authenticated else None,
                action="BULK_DELETE",
                changes={"deleted_count": count, "deleted_ids": [str(pk) for pk in ids]},
                request=self.request,
            )

        super().perform_bulk_destroy(queryset)
