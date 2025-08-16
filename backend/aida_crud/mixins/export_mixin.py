from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from ..exporters import DataExporter
from ..audit.models import AuditLog


class ExportMixin:
    """Mixin for data export functionality"""

    export_formats = ["csv", "json", "xlsx"]
    export_fields = None

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        """Export filtered data in various formats"""
        format = request.query_params.get("format", "csv").lower()

        if format not in self.export_formats:
            return Response(
                {"error": f"Unsupported format. Supported formats: {self.export_formats}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.filter_queryset(self.get_queryset())

        fields = self.export_fields
        if not fields:
            requested_fields = request.query_params.get("fields")
            if requested_fields:
                fields = requested_fields.split(",")

        filename = request.query_params.get("filename")
        if not filename:
            model_name = self.get_serializer_class().Meta.model.__name__.lower()
            filename = f"{model_name}_export"

        if hasattr(request, "user") and request.user.is_authenticated:
            AuditLog.log_action(
                user=request.user,
                action="EXPORT",
                changes={"format": format, "count": queryset.count(), "fields": fields},
                request=request,
            )

        return DataExporter.export(
            queryset=queryset, format=format, fields=fields, filename=filename
        )

    @action(detail=False, methods=["get"], url_path="export-options")
    def export_options(self, request):
        """Get available export options"""
        model = self.get_serializer_class().Meta.model
        fields = [f.name for f in model._meta.fields]

        return Response(
            {
                "formats": self.export_formats,
                "fields": fields,
                "default_fields": self.export_fields or fields,
                "max_export_size": getattr(self, "max_export_size", 10000),
            }
        )
