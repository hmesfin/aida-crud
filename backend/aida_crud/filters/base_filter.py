import django_filters
from functools import reduce
from django.db import models
from rest_framework.filters import OrderingFilter as DRFOrderingFilter
from rest_framework.filters import SearchFilter as DRFSearchFilter


class AidaFilterSet(django_filters.FilterSet):
    """Enhanced FilterSet with common filters."""

    created_at_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte", label="Created after"
    )
    created_at_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte", label="Created before"
    )
    updated_at_after = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gte", label="Updated after"
    )
    updated_at_before = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="lte", label="Updated before"
    )

    class Meta:
        abstract = True
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            models.BooleanField: {
                "filter_class": django_filters.BooleanFilter,
            },
            models.DateField: {
                "filter_class": django_filters.DateFilter,
            },
            models.DateTimeField: {
                "filter_class": django_filters.DateTimeFilter,
            },
            models.UUIDField: {
                "filter_class": django_filters.UUIDFilter,
            },
        }

    @classmethod
    def get_filters(cls):
        """Get filter fields information for metadata"""
        filters = {}
        for name, filter_field in cls.base_filters.items():
            filters[name] = {
                "type": filter_field.__class__.__name__,
                "label": filter_field.label or name.replace("_", " ").title(),
                "lookup_expr": filter_field.lookup_expr,
                "field_name": filter_field.field_name,
            }
        return filters


class SearchFilter(DRFSearchFilter):
    """Enhanced search filter with additional features"""

    def get_search_fields(self, view, request):
        """Allow dynamic search fields from request"""
        search_fields = super().get_search_fields(view, request)

        requested_fields = request.query_params.get("search_fields", None)
        if requested_fields:
            requested_fields = requested_fields.split(",")
            model_fields = [f.name for f in view.queryset.model._meta.fields]
            valid_fields = [f for f in requested_fields if f in model_fields]
            if valid_fields:
                return valid_fields

        return search_fields

    def filter_queryset(self, request, queryset, view):
        """Enhanced filtering with field-specific search"""
        search_terms = self.get_search_terms(request)
        if not search_terms:
            return queryset

        search_type = request.query_params.get("search_type", "contains")

        if search_type == "exact":
            return self._exact_search(queryset, search_terms, view, request)
        elif search_type == "startswith":
            return self._prefix_search(queryset, search_terms, view, request)
        else:
            return super().filter_queryset(request, queryset, view)

    def _exact_search(self, queryset, search_terms, view, request):
        """Perform exact match search."""
        search_fields = self.get_search_fields(view, request)
        orm_lookups = ["%s__exact" % f for f in search_fields]

        for search_term in search_terms:
            queries = [models.Q(**{orm_lookup: search_term}) for orm_lookup in orm_lookups]
            queryset = queryset.filter(reduce(lambda x, y: x | y, queries))

        return queryset

    def _prefix_search(self, queryset, search_terms, view, request):
        """Perform prefix search."""
        search_fields = self.get_search_fields(view, request)
        orm_lookups = ["%s__istartswith" % f for f in search_fields]

        for search_term in search_terms:
            queries = [models.Q(**{orm_lookup: search_term}) for orm_lookup in orm_lookups]
            queryset = queryset.filter(reduce(lambda x, y: x | y, queries))

        return queryset


class OrderingFilter(DRFOrderingFilter):
    """Enhanced ordering filter with additional features"""

    def get_ordering(self, request, queryset, view):
        """Support multiple ordering with field validation"""
        ordering = super().get_ordering(request, queryset, view)

        if ordering:
            model_fields = [f.name for f in queryset.model._meta.fields]
            valid_ordering = []

            for field in ordering:
                field_name = field.lstrip("-")
                if field_name in model_fields:
                    valid_ordering.append(field)
                elif "__" in field_name:
                    valid_ordering.append(field)

            return valid_ordering if valid_ordering else ordering

        return ordering

    def filter_queryset(self, request, queryset, view):
        """Apply ordering with null value handling"""
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            nulls_last = request.query_params.get("nulls_last", "false").lower() == "true"

            if nulls_last:
                new_ordering = []
                for field in ordering:
                    if field.startswith("-"):
                        new_ordering.append(models.F(field[1:]).desc(nulls_last=True))
                    else:
                        new_ordering.append(models.F(field).asc(nulls_last=True))
                return queryset.order_by(*new_ordering)

            return queryset.order_by(*ordering)

        return queryset
