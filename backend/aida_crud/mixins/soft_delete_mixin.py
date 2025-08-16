from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone


class SoftDeleteMixin:
    """Mixin for soft delete functionality in viewsets"""

    def get_queryset(self):
        """Override to handle deleted items visibility"""
        queryset = super().get_queryset()

        if self.action == "deleted":
            return queryset.model.objects.dead()
        elif self.action == "with_deleted":
            return queryset.model.objects.with_deleted()
        elif self.request.query_params.get("include_deleted", "false").lower() == "true":
            return queryset.model.objects.with_deleted()

        return queryset

    def perform_destroy(self, instance):
        """Soft delete by default"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        if hasattr(self.request, "user"):
            instance.deleted_by = self.request.user
        instance.save()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """Restore a soft-deleted object"""
        instance = self.get_object()

        if not instance.is_deleted:
            return Response({"error": "Object is not deleted"}, status=status.HTTP_400_BAD_REQUEST)

        instance.is_deleted = False
        instance.deleted_at = None
        instance.deleted_by = None
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["delete"], url_path="hard-delete")
    def hard_delete(self, request, pk=None):
        """Permanently delete an object"""
        instance = self.get_object()
        instance.delete(hard=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="deleted")
    def deleted(self, request):
        """List soft-deleted objects"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="bulk-restore")
    def bulk_restore(self, request):
        """Bulk restore soft-deleted objects"""
        ids = request.data.get("ids", [])

        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().model.objects.dead().filter(id__in=ids)
        count = queryset.count()

        queryset.update(is_deleted=False, deleted_at=None, deleted_by=None)

        return Response({"restored": count, "ids": ids})

    @action(detail=False, methods=["delete"], url_path="empty-trash")
    def empty_trash(self, request):
        """Permanently delete all soft-deleted objects"""
        queryset = self.get_queryset().model.objects.dead()
        count = queryset.count()
        queryset.hard_delete()

        return Response({"permanently_deleted": count}, status=status.HTTP_204_NO_CONTENT)
