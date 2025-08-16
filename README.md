# AIDA-CRUD Framework

**Advanced Intelligent Django API CRUD Framework**

A comprehensive, DRY solution for building feature-rich CRUD operations across Django REST Framework and Vue.js applications. AIDA-CRUD provides generic, reusable components that automatically configure themselves based on API metadata, eliminating repetitive code patterns.

## Features

### Backend (Django)

- ✅ Generic viewsets with automatic CRUD operations
- ✅ Context-aware serializers with dynamic field selection
- ✅ Advanced filtering, searching, and ordering
- ✅ Bulk operations (create, update, delete)
- ✅ Soft delete functionality
- ✅ Comprehensive audit trail system
- ✅ Multi-format export (CSV, JSON, Excel)
- ✅ API metadata for frontend auto-configuration
- ✅ User tracking (created_by, updated_by)
- ✅ Optimized database queries

### Frontend (Vue.js)

- ✅ Composable CRUD hooks (useCrud)
- ✅ Auto-configuring data tables
- ✅ Dynamic forms with validation
- ✅ Bulk selection and operations
- ✅ Export functionality
- ✅ Pagination, sorting, and search
- ✅ TypeScript support

## Installation

### Backend

```bash
pip install aida-crud
# or add to requirements.txt
```

### Frontend

```bash
npm install @aida/crud
# or
yarn add @aida/crud
```

## Quick Start

### Django Backend Setup

#### 1. Configure Django Settings

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_filters',
    'aida_crud',
    # ...
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'aida_crud.filters.SearchFilter',
        'aida_crud.filters.OrderingFilter',
    ],
    'DEFAULT_METADATA_CLASS': 'aida_crud.core.AidaMetadata',
}
```

#### 2. Create Your Models

```python
# models.py
from aida_crud.core import AidaBaseModel, SoftDeleteModel
from aida_crud.core import AidaManager, SoftDeleteManager

class Product(SoftDeleteModel):
    """Example model with all AIDA-CRUD features"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)
    
    objects = SoftDeleteManager()
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name
```

#### 3. Create Serializers

```python
# serializers.py
from aida_crud.serializers import AidaModelSerializer

class ProductSerializer(AidaModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
```

#### 4. Create ViewSets

```python
# views.py
from aida_crud.viewsets import AidaModelViewSet
from aida_crud.filters import AidaFilterSet
import django_filters

class ProductFilterSet(AidaFilterSet):
    """Custom filters for Product"""
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.MultipleChoiceFilter(choices=CATEGORY_CHOICES)
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'is_active']

class ProductViewSet(AidaModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilterSet
    
    # Configure list display
    list_display = ['name', 'category', 'price', 'stock_quantity', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = '__all__'
    
    # Enable bulk operations
    bulk_actions = ['delete', 'archive', 'activate', 'deactivate']
    
    # Configure export
    export_formats = ['csv', 'json', 'xlsx']
    export_fields = ['name', 'category', 'price', 'stock_quantity']
    
    # Add computed fields
    computed_fields = {
        'status': lambda obj: 'In Stock' if obj.stock_quantity > 0 else 'Out of Stock',
        'formatted_price': lambda obj: f'${obj.price:.2f}'
    }
    
    # Custom bulk actions
    def bulk_archive(self, queryset, **kwargs):
        count = queryset.update(is_active=False, stock_quantity=0)
        return {'archived': count}
```

#### 5. Configure URLs

```python
# urls.py
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

### Vue.js Frontend Setup

#### 1. Basic Usage with Composable

```vue
<template>
  <div>
    <!-- Auto-configured data table -->
    <AidaTable
      :items="state.items"
      :columns="columns"
      :loading="state.loading"
      :total="state.pagination.total"
      :current-page="state.pagination.page"
      :page-size="state.pagination.pageSize"
      selectable
      exportable
      @search="setSearch"
      @sort="setOrdering"
      @page-change="setPage"
      @create="showCreateDialog"
      @edit="showEditDialog"
      @delete="handleDelete"
      @export="exportData"
      @bulk-action="handleBulkAction"
    />
    
    <!-- Dynamic form dialog -->
    <dialog v-if="showForm" @close="showForm = false">
      <AidaForm
        :fields="formFields"
        :initial-data="currentItem"
        @submit="handleSave"
        @cancel="showForm = false"
      />
    </dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCrud } from '@aida/crud'
import { AidaTable, AidaForm } from '@aida/crud/components'

const { 
  state, 
  fetchMetadata,
  fetchItems,
  createItem,
  updateItem,
  deleteItem,
  bulkDelete,
  exportData,
  setSearch,
  setOrdering,
  setPage
} = useCrud('/api/products/')

const showForm = ref(false)
const currentItem = ref(null)
const formFields = ref([])
const columns = ref([])

onMounted(async () => {
  // Fetch metadata to auto-configure components
  const metadata = await fetchMetadata()
  
  // Auto-generate columns from metadata
  columns.value = metadata.list_display.map(field => ({
    key: field,
    label: metadata.fields[field]?.label || field,
    sortable: metadata.ordering_fields.includes(field),
    type: metadata.fields[field]?.type
  }))
  
  // Auto-generate form fields from metadata
  formFields.value = Object.entries(metadata.fields)
    .filter(([key, field]) => field.editable)
    .map(([key, field]) => ({
      name: key,
      ...field
    }))
})

function showCreateDialog() {
  currentItem.value = null
  showForm.value = true
}

function showEditDialog(item) {
  currentItem.value = item
  showForm.value = true
}

async function handleSave(data) {
  if (currentItem.value) {
    await updateItem(currentItem.value.id, data)
  } else {
    await createItem(data)
  }
  showForm.value = false
}

async function handleDelete(item) {
  if (confirm(`Delete ${item.name}?`)) {
    await deleteItem(item.id)
  }
}

async function handleBulkAction(items) {
  const action = prompt('Select action: delete, archive, activate')
  if (action === 'delete') {
    if (confirm(`Delete ${items.length} items?`)) {
      await bulkDelete(items.map(i => i.id))
    }
  }
}
</script>
```

#### 2. Advanced Features

```javascript
// Advanced filtering and search
const { state, setFilter, clearFilters } = useCrud('/api/products/')

// Apply multiple filters
await setFilter('category', 'electronics')
await setFilter('min_price', 100)
await setFilter('is_active', true)

// Clear all filters
await clearFilters()

// Bulk operations
await bulkCreate([
  { name: 'Product 1', price: 99.99 },
  { name: 'Product 2', price: 149.99 }
])

await bulkUpdate([
  { id: 1, price: 89.99 },
  { id: 2, price: 139.99 }
])

await bulkAction('archive', [1, 2, 3], { reason: 'Discontinued' })

// Soft delete and restore
await deleteItem(1) // Soft delete
await restoreItem(1) // Restore

// Export data
await exportData('xlsx', ['name', 'price', 'category'])
```

## API Endpoints

AIDA-CRUD automatically provides these endpoints for each viewset:

### Standard CRUD

- `GET /api/resource/` - List with pagination, filtering, search
- `POST /api/resource/` - Create new item
- `GET /api/resource/{id}/` - Retrieve single item
- `PUT /api/resource/{id}/` - Update item (full)
- `PATCH /api/resource/{id}/` - Update item (partial)
- `DELETE /api/resource/{id}/` - Delete item (soft delete by default)

### Bulk Operations

- `POST /api/resource/bulk-create/` - Create multiple items
- `PUT /api/resource/bulk-update/` - Update multiple items
- `POST /api/resource/bulk-delete/` - Delete multiple items
- `POST /api/resource/bulk-action/` - Custom bulk actions

### Soft Delete

- `POST /api/resource/{id}/restore/` - Restore soft-deleted item
- `DELETE /api/resource/{id}/hard-delete/` - Permanently delete
- `GET /api/resource/deleted/` - List deleted items
- `POST /api/resource/bulk-restore/` - Bulk restore
- `DELETE /api/resource/empty-trash/` - Permanently delete all

### Export & Metadata

- `GET /api/resource/export/` - Export data (CSV, JSON, Excel)
- `OPTIONS /api/resource/metadata/` - Get model metadata
- `GET /api/resource/{id}/history/` - Get audit history
- `GET /api/resource/stats/` - Get statistics

## Advanced Configuration

### Custom Audit Trail

```python
# Track specific changes
from aida_crud.audit import AuditLog

class CustomViewSet(AidaModelViewSet):
    def perform_update(self, serializer):
        old_data = self.get_object().__dict__.copy()
        instance = serializer.save()
        
        # Log specific changes
        changes = {
            'field': field,
            'old': old_data[field],
            'new': getattr(instance, field)
        }
        for field in ['price', 'stock_quantity']:
            if old_data[field] != getattr(instance, field):
                AuditLog.log_action(
                    user=self.request.user,
                    action='PRICE_CHANGE' if field == 'price' else 'STOCK_CHANGE',
                    obj=instance,
                    changes=changes,
                    request=self.request
                )
```

### Dynamic Field Selection

```javascript
// Frontend: Request specific fields
const { fetchItems } = useCrud('/api/products/')

// Only fetch specific fields
await fetchItems({
  fields: 'id,name,price',
  exclude: 'description,created_by',
  expand: 'category,supplier' // Expand foreign keys
})
```

### Custom Export Formats

```python
from aida_crud.exporters import DataExporter

class CustomExporter(DataExporter):
    @staticmethod
    def export_pdf(queryset, fields=None, filename=None):
        # Custom PDF export implementation
        pass

class ProductViewSet(AidaModelViewSet):
    export_formats = ['csv', 'json', 'xlsx', 'pdf']
    
    def export(self, request):
        if request.query_params.get('format') == 'pdf':
            return CustomExporter.export_pdf(
                self.filter_queryset(self.get_queryset())
            )
        return super().export(request)
```

## Performance Optimization

### Backend Optimization

```python
class OptimizedViewSet(AidaModelViewSet):
    def get_queryset(self):
        # Optimize with select_related and prefetch_related
        return super().get_queryset()\
            .select_related('category', 'supplier')\
            .prefetch_related('tags', 'reviews')
    
    # Enable query result caching
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

### Frontend Optimization

```javascript
// Use pagination and lazy loading
const { state, setPageSize } = useCrud('/api/products/', {
  pageSize: 50,
  autoFetch: false // Manual control
})

// Debounced search
import { debounce } from '@vueuse/core'
const debouncedSearch = debounce(setSearch, 300)
```

## Testing

### Backend Tests

```python
from rest_framework.test import APITestCase
from aida_crud.tests import AidaCRUDTestMixin

class ProductAPITest(AidaCRUDTestMixin, APITestCase):
    endpoint = '/api/products/'
    model_class = Product
    
    def test_bulk_operations(self):
        # Test bulk create
        response = self.bulk_create([
            {'name': 'Product 1', 'price': 100},
            {'name': 'Product 2', 'price': 200}
        ])
        self.assertEqual(response.status_code, 201)
        
    def test_soft_delete(self):
        obj = self.create_test_object()
        self.soft_delete(obj.id)
        self.assertTrue(obj.is_deleted)
        self.restore(obj.id)
        self.assertFalse(obj.is_deleted)
```

## Requirements

### Backend

- Python 3.8+
- Django 3.2+
- Django REST Framework 3.12+
- django-filter 2.4+
- openpyxl 3.0+ (for Excel export)

### Frontend

- Vue.js 3.3+
- TypeScript 4.5+ (optional)
- Axios 1.0+

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the maintainers.
