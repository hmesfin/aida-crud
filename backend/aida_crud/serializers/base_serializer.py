from rest_framework import serializers
from django.db import models


class DynamicFieldsSerializer(serializers.ModelSerializer):
    """Serializer with dynamic field selection based on context"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        context = kwargs.get("context", {})
        request = context.get("request", None)

        if request:
            fields = request.query_params.get("fields", None)
            exclude = request.query_params.get("exclude", None)
            expand = request.query_params.get("expand", None)

            if fields:
                fields = fields.split(",")
                allowed = set(fields)
                existing = set(self.fields)
                for field_name in existing - allowed:
                    self.fields.pop(field_name)

            if exclude:
                exclude = exclude.split(",")
                for field_name in exclude:
                    self.fields.pop(field_name, None)

            if expand:
                self._expand_fields(expand.split(","))

    def _expand_fields(self, expand_fields):
        """Expand related fields for nested serialization"""
        for field_name in expand_fields:
            if field_name in self.fields:
                field = self.fields[field_name]
                if isinstance(field, serializers.PrimaryKeyRelatedField):
                    model = field.queryset.model
                    self.fields[field_name] = self._get_nested_serializer(model)(read_only=True)

    def _get_nested_serializer(self, model):
        """Generate a nested serializer for related models"""

        class NestedSerializer(serializers.ModelSerializer):
            class Meta:
                model = model
                fields = "__all__"

        return NestedSerializer


class AidaModelSerializer(DynamicFieldsSerializer):
    """Enhanced ModelSerializer with additional features"""

    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    updated_by_username = serializers.CharField(source="updated_by.username", read_only=True)

    class Meta:
        abstract = True
        read_only_fields = ["id", "created_at", "updated_at", "created_by", "updated_by"]

    def create(self, validated_data):
        """Set created_by and updated_by on creation"""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user
            validated_data["updated_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Set updated_by on update"""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["updated_by"] = request.user
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Add computed fields to representation"""
        data = super().to_representation(instance)

        if self.context.get("request"):
            view = self.context.get("view")
            if view and hasattr(view, "computed_fields"):
                for field_name, compute_func in view.computed_fields.items():
                    data[field_name] = compute_func(instance)

        return data

    @classmethod
    def get_field_info(cls):
        """Return field information for frontend configuration"""
        field_info = {}
        for field_name, field in cls._declared_fields.items():
            info = {
                "type": field.__class__.__name__,
                "required": field.required,
                "read_only": field.read_only,
                "label": field.label or field_name.replace("_", " ").title(),
                "help_text": field.help_text or "",
            }

            if hasattr(field, "choices"):
                info["choices"] = field.choices

            field_info[field_name] = info

        return field_info
