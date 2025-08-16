from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction


class BulkOperationMixin:
    """Mixin for bulk operations on viewsets"""

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """Bulk create multiple objects"""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.perform_bulk_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put", "patch"], url_path="bulk-update")
    def bulk_update(self, request):
        """Bulk update multiple objects"""
        partial = request.method == "PATCH"

        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of objects"}, status=status.HTTP_400_BAD_REQUEST
            )

        ids = [item.get("id") for item in request.data if item.get("id")]
        instances = self.get_queryset().filter(id__in=ids)

        serializer = self.get_serializer(instances, data=request.data, many=True, partial=partial)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.perform_bulk_update(serializer)

        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        """Bulk delete multiple objects"""
        ids = request.data.get("ids", [])

        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(id__in=ids)
        count = queryset.count()

        with transaction.atomic():
            self.perform_bulk_destroy(queryset)

        return Response({"deleted": count, "ids": ids}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="bulk-action")
    def bulk_action(self, request):
        """Perform custom bulk action"""
        action_name = request.data.get("action")
        ids = request.data.get("ids", [])
        params = request.data.get("params", {})

        if not action_name:
            return Response({"error": "No action specified"}, status=status.HTTP_400_BAD_REQUEST)

        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        handler = getattr(self, f"bulk_{action_name}", None)
        if not handler:
            return Response(
                {"error": f"Unknown action: {action_name}"}, status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(id__in=ids)

        with transaction.atomic():
            result = handler(queryset, **params)

        return Response(result)

    def perform_bulk_create(self, serializer):
        """Perform the bulk creation"""
        serializer.save()

    def perform_bulk_update(self, serializer):
        """Perform the bulk update"""
        serializer.save()

    def perform_bulk_destroy(self, queryset):
        """Perform the bulk deletion"""
        queryset.delete()

    def bulk_archive(self, queryset, **kwargs):
        """Example bulk action: archive objects"""
        count = queryset.update(is_archived=True)
        return {"archived": count}

    def bulk_activate(self, queryset, **kwargs):
        """Example bulk action: activate objects"""
        count = queryset.update(is_active=True)
        return {"activated": count}

    def bulk_deactivate(self, queryset, **kwargs):
        """Example bulk action: deactivate objects"""
        count = queryset.update(is_active=False)
        return {"deactivated": count}
