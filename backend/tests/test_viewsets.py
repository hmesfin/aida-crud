"""Test suite for AIDA-CRUD viewsets."""

import json
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIRequestFactory
from unittest.mock import Mock, patch, MagicMock

from aida_crud.viewsets import AidaModelViewSet
from aida_crud.serializers import AidaModelSerializer

User = get_user_model()


# Mock model for testing
class MockModel:
    """Mock model for testing."""

    id = 1
    name = "Test"
    is_deleted = False

    class Meta:
        verbose_name = "Mock Model"
        verbose_name_plural = "Mock Models"


# Mock serializer for testing
class MockSerializer(AidaModelSerializer):
    """Mock serializer for testing."""

    class Meta:
        model = MockModel
        fields = "__all__"


@pytest.mark.django_db
class TestAidaModelViewSet:
    """Test AidaModelViewSet functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.viewset = AidaModelViewSet()
        self.viewset.basename = "mockmodel"
        self.viewset.serializer_class = MockSerializer
        self.viewset.queryset = Mock()

    def test_metadata_endpoint(self, user):
        """Test metadata endpoint returns proper structure."""
        request = self.factory.options("/api/mockmodel/metadata/")
        request.user = user

        # Mock the viewset methods
        self.viewset.request = request
        self.viewset.get_serializer_class = Mock(return_value=MockSerializer)

        with patch.object(self.viewset.metadata_class, "determine_metadata") as mock_metadata:
            mock_metadata.return_value = {
                "name": "MockModel",
                "fields": {},
            }

            response = self.viewset.metadata(request)

            assert response.status_code == 200
            assert "model_name" in response.data
            assert "list_display" in response.data
            assert "bulk_actions" in response.data
            assert "export_formats" in response.data

    @pytest.mark.parametrize(
        "action,expected_count",
        [
            ("list", 1),
            ("deleted", 0),
            ("with_deleted", 2),
        ],
    )
    def test_soft_delete_queryset_filtering(self, action, expected_count):
        """Test queryset filtering based on action."""
        self.viewset.action = action
        self.viewset.request = Mock()
        self.viewset.request.query_params = Mock()
        self.viewset.request.query_params.get = Mock(return_value="false")

        # Mock the model's objects manager
        mock_model = Mock()
        mock_model.objects.dead = Mock()
        mock_model.objects.with_deleted = Mock()

        self.viewset.queryset = Mock()
        self.viewset.queryset.model = mock_model

        # Test get_queryset returns appropriate queryset
        if action == "deleted":
            self.viewset.get_queryset()
            mock_model.objects.dead.assert_called_once()
        elif action == "with_deleted":
            self.viewset.get_queryset()
            mock_model.objects.with_deleted.assert_called_once()

    def test_bulk_create_action(self, authenticated_client):
        """Test bulk create action."""
        data = [
            {"name": "Item 1"},
            {"name": "Item 2"},
            {"name": "Item 3"},
        ]

        with patch.object(AidaModelViewSet, "get_serializer") as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.is_valid = Mock(return_value=True)
            mock_serializer_instance.data = data
            mock_serializer.return_value = mock_serializer_instance

            viewset = AidaModelViewSet()
            viewset.request = Mock()
            viewset.request.data = data

            with patch.object(viewset, "perform_bulk_create"):
                response = viewset.bulk_create(viewset.request)

                assert response.status_code == status.HTTP_201_CREATED
                mock_serializer_instance.is_valid.assert_called_with(raise_exception=True)

    def test_bulk_delete_action(self, authenticated_client):
        """Test bulk delete action."""
        ids = [1, 2, 3]
        data = {"ids": ids}

        viewset = AidaModelViewSet()
        viewset.request = Mock()
        viewset.request.data = data

        mock_queryset = Mock()
        mock_queryset.count = Mock(return_value=3)
        viewset.get_queryset = Mock(return_value=mock_queryset)
        mock_queryset.filter = Mock(return_value=mock_queryset)

        with patch.object(viewset, "perform_bulk_destroy"):
            response = viewset.bulk_delete(viewset.request)

            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert response.data["deleted"] == 3
            assert response.data["ids"] == ids

    def test_export_action(self):
        """Test export action."""
        viewset = AidaModelViewSet()
        viewset.request = Mock()
        viewset.request.query_params = Mock()
        viewset.request.query_params.get = Mock(
            side_effect=lambda x, y=None: {"format": "csv"}.get(x, y)
        )

        mock_queryset = Mock()
        viewset.filter_queryset = Mock(return_value=mock_queryset)
        viewset.get_queryset = Mock(return_value=mock_queryset)
        viewset.get_serializer_class = Mock(return_value=MockSerializer)

        with patch("aida_crud.exporters.DataExporter.export") as mock_export:
            mock_export.return_value = Mock()
            response = viewset.export(viewset.request)

            mock_export.assert_called_once()
            assert mock_export.call_args[1]["format"] == "csv"

    def test_history_endpoint(self, user):
        """Test history endpoint for audit trail."""
        viewset = AidaModelViewSet()
        viewset.request = Mock()
        viewset.request.user = user

        mock_obj = Mock()
        viewset.get_object = Mock(return_value=mock_obj)

        with patch("aida_crud.audit.models.AuditLog.get_object_history") as mock_history:
            mock_log = Mock()
            mock_log.id = 1
            mock_log.action = "UPDATE"
            mock_log.user = user
            mock_log.timestamp = "2024-01-01"
            mock_log.changes = {}
            mock_log.ip_address = "127.0.0.1"

            mock_history.return_value = [mock_log]

            response = viewset.history(viewset.request, pk=1)

            assert response.status_code == 200
            assert len(response.data) == 1
            assert response.data[0]["action"] == "UPDATE"

    def test_stats_endpoint(self):
        """Test stats endpoint."""
        viewset = AidaModelViewSet()
        viewset.request = Mock()

        mock_queryset = Mock()
        mock_queryset.count = Mock(return_value=100)
        mock_queryset.filter = Mock(return_value=mock_queryset)

        viewset.filter_queryset = Mock(return_value=mock_queryset)
        viewset.get_queryset = Mock(return_value=mock_queryset)
        viewset.get_serializer_class = Mock(return_value=MockSerializer)

        # Mock the model
        mock_model = Mock()
        mock_model.objects.dead = Mock()
        mock_model.objects.dead().count = Mock(return_value=10)
        MockSerializer.Meta.model = mock_model

        response = viewset.stats(viewset.request)

        assert response.status_code == 200
        assert response.data["total"] == 100
        assert response.data["active"] == 100
