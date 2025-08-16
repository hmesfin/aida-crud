from rest_framework.metadata import SimpleMetadata
from rest_framework import serializers


class AidaMetadata(SimpleMetadata):
    """Enhanced metadata provider for frontend auto-configuration"""

    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)

        if hasattr(view, "get_serializer_class"):
            serializer_class = view.get_serializer_class()

            metadata["fields"] = self.get_serializer_fields(serializer_class())
            metadata["list_display"] = getattr(view, "list_display", [])
            metadata["list_filter"] = getattr(view, "list_filter", [])
            metadata["search_fields"] = getattr(view, "search_fields", [])
            metadata["ordering_fields"] = getattr(view, "ordering_fields", "__all__")
            metadata["bulk_actions"] = getattr(view, "bulk_actions", [])
            metadata["export_formats"] = getattr(view, "export_formats", ["csv", "json", "xlsx"])

            if hasattr(view, "filterset_class"):
                metadata["filters"] = self.get_filter_fields(view.filterset_class)

        metadata["permissions"] = (
            {
                "create": view.request.user.has_perm(f"{view.basename}.add"),
                "update": view.request.user.has_perm(f"{view.basename}.change"),
                "delete": view.request.user.has_perm(f"{view.basename}.delete"),
                "view": view.request.user.has_perm(f"{view.basename}.view"),
            }
            if hasattr(view, "basename")
            else {}
        )

        return metadata

    def get_serializer_fields(self, serializer):
        """Extract field information from serializer"""
        fields_info = {}

        for field_name, field in serializer.fields.items():
            field_info = {
                "type": field.__class__.__name__,
                "required": field.required,
                "read_only": field.read_only,
                "write_only": field.write_only,
                "label": field.label,
                "help_text": field.help_text,
                "allow_null": field.allow_null if hasattr(field, "allow_null") else False,
            }

            if isinstance(field, serializers.ChoiceField):
                field_info["choices"] = [
                    {"value": k, "display": v} for k, v in field.choices.items()
                ]

            if isinstance(field, serializers.CharField):
                field_info["max_length"] = getattr(field, "max_length", None)
                field_info["min_length"] = getattr(field, "min_length", None)

            if isinstance(field, (serializers.IntegerField, serializers.DecimalField)):
                field_info["max_value"] = getattr(field, "max_value", None)
                field_info["min_value"] = getattr(field, "min_value", None)

            if isinstance(field, serializers.ListField):
                field_info["child"] = {
                    "type": field.child.__class__.__name__ if field.child else None
                }

            if isinstance(field, serializers.PrimaryKeyRelatedField):
                field_info["model"] = field.queryset.model.__name__ if field.queryset else None

            fields_info[field_name] = field_info

        return fields_info

    def get_filter_fields(self, filterset_class):
        """Extract filter information"""
        filters_info = {}

        if filterset_class:
            for name, filter_field in filterset_class.base_filters.items():
                filters_info[name] = {
                    "type": filter_field.__class__.__name__,
                    "label": filter_field.label,
                    "lookup_expr": filter_field.lookup_expr,
                    "help_text": getattr(filter_field, "help_text", ""),
                }

        return filters_info
