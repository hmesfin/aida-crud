from rest_framework import serializers


class BulkSerializer(serializers.ListSerializer):
    """Serializer for bulk operations"""

    def create(self, validated_data):
        """Bulk create objects"""
        result = [self.child.create(attrs) for attrs in validated_data]

        try:
            if hasattr(self.child.Meta.model.objects, "bulk_create"):
                self.child.Meta.model.objects.bulk_create(result)
        except Exception:
            pass

        return result

    def update(self, instances, validated_data):
        """Bulk update objects"""
        instance_map = {instance.id: instance for instance in instances}
        result = []

        for item in validated_data:
            instance = instance_map.get(item.get("id"))
            if instance:
                result.append(self.child.update(instance, item))

        return result


class BulkOperationSerializer(serializers.Serializer):
    """Serializer for bulk operations requests"""

    ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="List of IDs to perform bulk operation on",
    )
    operation = serializers.ChoiceField(
        choices=["delete", "restore", "archive", "activate", "deactivate"],
        help_text="Bulk operation to perform",
    )
    data = serializers.JSONField(required=False, help_text="Additional data for the operation")
