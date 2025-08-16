from django.db import models
from django.db.models import Q


class AidaQuerySet(models.QuerySet):
    """Custom QuerySet with additional utility methods"""

    def search(self, query, fields=None):
        """Generic search across specified fields"""
        if not query:
            return self

        if not fields:
            fields = [
                f.name
                for f in self.model._meta.fields
                if isinstance(f, (models.CharField, models.TextField))
            ]

        q_objects = Q()
        for field in fields:
            q_objects |= Q(**{f"{field}__icontains": query})

        return self.filter(q_objects)

    def bulk_update_fields(self, updates):
        """Bulk update specific fields"""
        return self.update(**updates)

    def export_queryset(self, format="dict"):
        """Export queryset in various formats"""
        if format == "dict":
            return list(self.values())
        elif format == "list":
            return [[getattr(obj, f.name) for f in obj._meta.fields] for obj in self]
        return self


class AidaManager(models.Manager):
    """Enhanced manager with additional functionality"""

    def get_queryset(self):
        return AidaQuerySet(self.model, using=self._db)

    def search(self, query, fields=None):
        return self.get_queryset().search(query, fields)

    def bulk_create_with_user(self, objs, user=None, **kwargs):
        """Bulk create with user tracking"""
        if user:
            for obj in objs:
                obj.created_by = user
                obj.updated_by = user
        return self.bulk_create(objs, **kwargs)


class SoftDeleteQuerySet(AidaQuerySet):
    """QuerySet that excludes soft-deleted items by default"""

    def delete(self):
        """Soft delete all objects in queryset"""
        return self.update(is_deleted=True, deleted_at=models.functions.Now())

    def hard_delete(self):
        """Permanently delete objects"""
        return super().delete()

    def alive(self):
        """Return only non-deleted objects"""
        return self.filter(is_deleted=False)

    def dead(self):
        """Return only soft-deleted objects"""
        return self.filter(is_deleted=True)

    def with_deleted(self):
        """Return all objects including soft-deleted"""
        return self.all()


class SoftDeleteManager(AidaManager):
    """Manager that handles soft-deleted objects"""

    def get_queryset(self):
        """By default, exclude soft-deleted objects"""
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def dead(self):
        """Return only soft-deleted objects"""
        return SoftDeleteQuerySet(self.model, using=self._db).dead()

    def with_deleted(self):
        """Return all objects including soft-deleted"""
        return SoftDeleteQuerySet(self.model, using=self._db)
