"""Test suite for AIDA-CRUD models."""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import Mock, patch

from aida_crud.core import AidaBaseModel, SoftDeleteModel
from aida_crud.core.managers import AidaManager, SoftDeleteManager

User = get_user_model()


# Create test models for testing
class TestAidaModel(AidaBaseModel):
    """Test model for AidaBaseModel."""

    class Meta:
        app_label = "tests"


class TestSoftDeleteModel(SoftDeleteModel):
    """Test model for SoftDeleteModel."""

    objects = SoftDeleteManager()

    class Meta:
        app_label = "tests"


@pytest.mark.django_db
class TestAidaBaseModel:
    """Test AidaBaseModel functionality."""

    def test_model_creation(self):
        """Test basic model creation."""
        obj = TestAidaModel()
        assert obj.id is not None
        assert obj.created_at is None
        assert obj.updated_at is None

    def test_save_with_user_tracking(self, user):
        """Test save method with user tracking."""
        obj = TestAidaModel()
        obj._current_user = user
        obj.save()

        assert obj.created_by == user
        assert obj.updated_by == user
        assert obj.created_at is not None
        assert obj.updated_at is not None

    def test_update_with_user_tracking(self, user, admin_user):
        """Test updating with different user."""
        obj = TestAidaModel()
        obj._current_user = user
        obj.save()

        # Update with different user
        obj._current_user = admin_user
        obj.save()

        assert obj.created_by == user
        assert obj.updated_by == admin_user

    def test_get_field_metadata(self):
        """Test field metadata generation."""
        metadata = TestAidaModel.get_field_metadata()

        assert "id" in metadata
        assert "created_at" in metadata
        assert "updated_at" in metadata
        assert metadata["id"]["type"] == "UUIDField"
        assert metadata["id"]["required"] is False
        assert metadata["created_at"]["type"] == "DateTimeField"


@pytest.mark.django_db
class TestSoftDeleteModel:
    """Test SoftDeleteModel functionality."""

    def test_soft_delete(self, user):
        """Test soft delete functionality."""
        obj = TestSoftDeleteModel()
        obj._current_user = user
        obj.save()

        assert obj.is_deleted is False
        assert obj.deleted_at is None

        # Soft delete
        obj.delete()

        assert obj.is_deleted is True
        assert obj.deleted_at is not None
        assert TestSoftDeleteModel.objects.filter(id=obj.id).count() == 0
        assert TestSoftDeleteModel.objects.with_deleted().filter(id=obj.id).count() == 1

    def test_hard_delete(self, user):
        """Test hard delete functionality."""
        obj = TestSoftDeleteModel()
        obj._current_user = user
        obj.save()

        obj_id = obj.id
        obj.delete(hard=True)

        assert TestSoftDeleteModel.objects.with_deleted().filter(id=obj_id).count() == 0

    def test_restore(self, user):
        """Test restore functionality."""
        obj = TestSoftDeleteModel()
        obj._current_user = user
        obj.save()

        obj.delete()
        assert obj.is_deleted is True

        obj.restore()
        assert obj.is_deleted is False
        assert obj.deleted_at is None
        assert TestSoftDeleteModel.objects.filter(id=obj.id).count() == 1


@pytest.mark.django_db
class TestAidaManager:
    """Test AidaManager functionality."""

    def test_search_functionality(self):
        """Test search method."""
        # This would require a model with CharField/TextField
        # Implementation depends on actual model structure
        pass

    def test_bulk_create_with_user(self, user):
        """Test bulk create with user tracking."""
        objs = [
            TestAidaModel(),
            TestAidaModel(),
            TestAidaModel(),
        ]

        # Note: This would need actual implementation in manager
        # Currently testing the interface
        manager = AidaManager()
        manager.model = TestAidaModel

        # Test that method exists
        assert hasattr(manager, "bulk_create_with_user")


@pytest.mark.django_db
class TestSoftDeleteManager:
    """Test SoftDeleteManager functionality."""

    def test_queryset_excludes_deleted(self, user):
        """Test that default queryset excludes soft-deleted items."""
        # Create regular object
        obj1 = TestSoftDeleteModel()
        obj1._current_user = user
        obj1.save()

        # Create and delete object
        obj2 = TestSoftDeleteModel()
        obj2._current_user = user
        obj2.save()
        obj2.delete()

        assert TestSoftDeleteModel.objects.count() == 1
        assert TestSoftDeleteModel.objects.first().id == obj1.id

    def test_dead_queryset(self, user):
        """Test dead() returns only soft-deleted items."""
        # Create regular object
        obj1 = TestSoftDeleteModel()
        obj1._current_user = user
        obj1.save()

        # Create and delete object
        obj2 = TestSoftDeleteModel()
        obj2._current_user = user
        obj2.save()
        obj2.delete()

        dead_objects = TestSoftDeleteModel.objects.dead()
        assert dead_objects.count() == 1
        assert dead_objects.first().id == obj2.id

    def test_with_deleted_queryset(self, user):
        """Test with_deleted() returns all items."""
        # Create regular object
        obj1 = TestSoftDeleteModel()
        obj1._current_user = user
        obj1.save()

        # Create and delete object
        obj2 = TestSoftDeleteModel()
        obj2._current_user = user
        obj2.save()
        obj2.delete()

        all_objects = TestSoftDeleteModel.objects.with_deleted()
        assert all_objects.count() == 2
