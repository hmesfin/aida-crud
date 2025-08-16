# AIDA-CRUD

**Advanced Intelligent Django API CRUD Framework**

A comprehensive, DRY solution for building feature-rich CRUD operations in Django REST Framework applications.

## Installation

```bash
pip install aida-crud
```

## Quick Start

### 1. Add to Django Settings

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_filters',
    'aida_crud',
]
```

### 2. Create Your Models

```python
from aida_crud.core import SoftDeleteModel

class Product(SoftDeleteModel):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['-created_at']
```

### 3. Create Serializers

```python
from aida_crud.serializers import AidaModelSerializer

class ProductSerializer(AidaModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
```

### 4. Create ViewSets

```python
from aida_crud.viewsets import AidaModelViewSet

class ProductViewSet(AidaModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    search_fields = ['name', 'description']
    ordering_fields = '__all__'
```

## Features

### Backend Capabilities

- ✅ **Generic ViewSets** - Automatic CRUD operations with minimal code
- ✅ **Dynamic Serializers** - Context-aware field selection and expansion
- ✅ **Advanced Filtering** - Built-in search, ordering, and filtering
- ✅ **Bulk Operations** - Create, update, and delete multiple records
- ✅ **Soft Delete** - Safe deletion with restore capabilities
- ✅ **Audit Trail** - Comprehensive activity logging
- ✅ **Data Export** - CSV, JSON, and Excel export support
- ✅ **API Metadata** - Auto-configuration endpoints for frontends

### Built-in Endpoints

Each ViewSet automatically provides:

- `GET /api/resource/` - List with pagination
- `POST /api/resource/` - Create new item
- `GET /api/resource/{id}/` - Retrieve item
- `PUT/PATCH /api/resource/{id}/` - Update item
- `DELETE /api/resource/{id}/` - Soft delete item
- `POST /api/resource/bulk-create/` - Bulk create
- `POST /api/resource/bulk-update/` - Bulk update
- `POST /api/resource/bulk-delete/` - Bulk delete
- `GET /api/resource/export/` - Export data
- `OPTIONS /api/resource/metadata/` - Get metadata

## Advanced Usage

### Custom Filters

```python
from aida_crud.filters import AidaFilterSet

class ProductFilterSet(AidaFilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'is_active']
```

### Audit Logging

```python
from aida_crud.audit import AuditLog

# Automatic logging in ViewSets
class ProductViewSet(AidaModelViewSet):
    # All CRUD operations are automatically logged
    pass

# Manual logging
AuditLog.log_action(
    user=request.user,
    action='CUSTOM_ACTION',
    obj=product,
    changes={'price': {'old': 100, 'new': 150}}
)
```

### Bulk Operations

```python
# In your ViewSet
class ProductViewSet(AidaModelViewSet):
    bulk_actions = ['archive', 'activate', 'deactivate']
    
    def bulk_archive(self, queryset, **kwargs):
        count = queryset.update(is_archived=True)
        return {'archived': count}
```

## Configuration

### ViewSet Options

```python
class MyViewSet(AidaModelViewSet):
    # Display configuration
    list_display = ['name', 'price', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = '__all__'
    ordering = ['-created_at']
    
    # Bulk operations
    bulk_actions = ['delete', 'archive', 'activate']
    
    # Export configuration
    export_formats = ['csv', 'json', 'xlsx']
    export_fields = ['name', 'price', 'category']
    
    # Computed fields
    computed_fields = {
        'display_price': lambda obj: f'${obj.price:.2f}'
    }
```

## Requirements

- Python 3.8+
- Django 3.2+
- Django REST Framework 3.12+
- django-filter 2.4+

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please visit our [GitHub repository](https://github.com/hmesfin/aida-crud).

## Support

For issues and questions, please use our [GitHub Issues](https://github.com/hmesfin/aida-crud/issues).