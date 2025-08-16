from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..filters import SearchFilter, OrderingFilter
from ..mixins import BulkOperationMixin, SoftDeleteMixin, ExportMixin, AuditMixin
from ..core import AidaMetadata


class AidaModelViewSet(
    BulkOperationMixin, SoftDeleteMixin, ExportMixin, AuditMixin, viewsets.ModelViewSet
):
    """
    Enhanced ModelViewSet with all AIDA-CRUD features

    Features:
    - Dynamic field selection
    - Advanced filtering, searching, ordering
    - Bulk operations
    - Soft delete
    - Audit trail
    - Data export
    - Metadata for frontend auto-configuration
    """

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    metadata_class = AidaMetadata

    list_display = []
    list_filter = []
    search_fields = []
    ordering_fields = "__all__"
    ordering = ["-created_at"]

    computed_fields = {}

    bulk_actions = ["delete", "archive", "activate", "deactivate"]

    export_formats = ["csv", "json", "xlsx"]
    export_fields = None

    max_export_size = 10000

    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context["request"] = self.request
        context["view"] = self
        return context

    @action(detail=False, methods=["options"], url_path="metadata")
    def metadata(self, request):
        """Enhanced metadata endpoint for frontend configuration"""
        metadata = self.metadata_class().determine_metadata(request, self)

        model = self.get_serializer_class().Meta.model

        metadata.update(
            {
                "model_name": model.__name__,
                "verbose_name": model._meta.verbose_name,
                "verbose_name_plural": model._meta.verbose_name_plural,
                "list_display": self.list_display or [f.name for f in model._meta.fields][:5],
                "list_filter": self.list_filter,
                "search_fields": self.search_fields,
                "ordering_fields": self.ordering_fields,
                "default_ordering": self.ordering,
                "bulk_actions": self.bulk_actions,
                "export_formats": self.export_formats,
                "has_soft_delete": hasattr(model, "is_deleted"),
                "computed_fields": list(self.computed_fields.keys()),
            }
        )

        if hasattr(model, "get_field_metadata"):
            metadata["model_fields"] = model.get_field_metadata()

        return Response(metadata)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Get audit history for an object"""
        from ..audit.models import AuditLog

        obj = self.get_object()
        logs = AuditLog.get_object_history(obj)

        data = []
        for log in logs:
            data.append(
                {
                    "id": log.id,
                    "action": log.action,
                    "user": log.user.username if log.user else "System",
                    "timestamp": log.timestamp,
                    "changes": log.changes,
                    "ip_address": log.ip_address,
                }
            )

        return Response(data)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Get statistics about the model"""
        queryset = self.filter_queryset(self.get_queryset())
        model = self.get_serializer_class().Meta.model

        stats = {
            "total": queryset.count(),
            "active": queryset.count(),
        }

        if hasattr(model, "is_deleted"):
            stats["deleted"] = model.objects.dead().count()
            stats["active"] = queryset.filter(is_deleted=False).count()

        if hasattr(model, "is_active"):
            stats["inactive"] = queryset.filter(is_active=False).count()

        return Response(stats)
