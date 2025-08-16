<template>
  <div class="w-full">
    <!-- Toolbar -->
    <div v-if="showToolbar" class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
      <!-- Search -->
      <div v-if="searchable" class="w-full sm:w-auto">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          :placeholder="searchPlaceholder"
          class="form-input min-w-[250px]"
        />
      </div>
      
      <!-- Actions -->
      <div class="flex flex-wrap items-center gap-2">
        <button
          v-if="hasSelection"
          @click="$emit('bulk-action', selectedItems)"
          class="btn btn-secondary"
        >
          <span class="hidden sm:inline">Bulk Actions</span>
          <span class="badge badge-primary ml-2">{{ selectedItems.length }}</span>
        </button>
        
        <select
          v-if="exportable && exportFormats.length"
          @change="handleExport"
          class="form-select text-sm"
        >
          <option value="">Export as...</option>
          <option v-for="format in exportFormats" :key="format" :value="format">
            {{ format.toUpperCase() }}
          </option>
        </select>
        
        <button
          v-if="creatable"
          @click="$emit('create')"
          class="btn btn-primary"
        >
          {{ createButtonText }}
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table">
          <thead class="table-header">
            <tr>
              <th v-if="selectable" class="table-header-cell w-12">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  @change="toggleSelectAll"
                  class="form-checkbox"
                />
              </th>
              
              <th
                v-for="column in visibleColumns"
                :key="column.key"
                :class="[
                  'table-header-cell',
                  column.sortable && 'cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-800',
                  column.align === 'center' && 'text-center',
                  column.align === 'right' && 'text-right'
                ]"
                @click="column.sortable ? handleSort(column.key) : null"
              >
                <div class="flex items-center justify-between">
                  <span>{{ column.label }}</span>
                  <span v-if="column.sortable" class="ml-2 text-gray-400">
                    <svg v-if="ordering === column.key" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
                    </svg>
                    <svg v-else-if="ordering === `-${column.key}`" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z"/>
                    </svg>
                    <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L10 5.414 7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3zm-3.707 9.293a1 1 0 011.414 0L10 14.586l2.293-2.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"/>
                    </svg>
                  </span>
                </div>
              </th>
              
              <th v-if="showActions" class="table-header-cell text-right">
                Actions
              </th>
            </tr>
          </thead>
          
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <!-- Loading State -->
            <tr v-if="loading">
              <td :colspan="totalColumns" class="table-cell text-center py-12">
                <div class="flex flex-col items-center justify-center space-y-4">
                  <svg class="spinner w-8 h-8" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span class="text-gray-500 dark:text-gray-400">Loading...</span>
                </div>
              </td>
            </tr>
            
            <!-- Empty State -->
            <tr v-else-if="!items.length">
              <td :colspan="totalColumns" class="table-cell text-center py-12">
                <div class="text-gray-500 dark:text-gray-400">
                  {{ emptyText }}
                </div>
              </td>
            </tr>
            
            <!-- Data Rows -->
            <tr
              v-else
              v-for="item in items"
              :key="getItemKey(item)"
              :class="[
                'hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors',
                isSelected(item) && 'bg-emerald-50 dark:bg-emerald-900/20'
              ]"
              @click="handleRowClick(item)"
            >
              <td v-if="selectable" class="table-cell w-12">
                <input
                  type="checkbox"
                  :checked="isSelected(item)"
                  @click.stop
                  @change="toggleSelect(item)"
                  class="form-checkbox"
                />
              </td>
              
              <td
                v-for="column in visibleColumns"
                :key="column.key"
                :class="[
                  'table-cell',
                  column.align === 'center' && 'text-center',
                  column.align === 'right' && 'text-right'
                ]"
              >
                <slot :name="`cell-${column.key}`" :item="item" :value="getItemValue(item, column)">
                  {{ formatValue(getItemValue(item, column), column) }}
                </slot>
              </td>
              
              <td v-if="showActions" class="table-cell text-right">
                <slot name="actions" :item="item">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      v-if="editable"
                      @click.stop="$emit('edit', item)"
                      class="btn btn-ghost btn-sm"
                    >
                      Edit
                    </button>
                    <button
                      v-if="deletable"
                      @click.stop="$emit('delete', item)"
                      class="btn btn-ghost btn-sm text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                    >
                      Delete
                    </button>
                  </div>
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="paginated && total > 0" class="flex flex-col sm:flex-row justify-between items-center gap-4 mt-6">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        Showing <span class="font-medium">{{ paginationInfo.start }}</span> to 
        <span class="font-medium">{{ paginationInfo.end }}</span> of 
        <span class="font-medium">{{ total }}</span> results
      </div>
      
      <div class="flex items-center gap-2">
        <button
          @click="$emit('page-change', currentPage - 1)"
          :disabled="currentPage === 1"
          class="btn btn-secondary btn-sm"
        >
          Previous
        </button>
        
        <div class="hidden sm:flex items-center gap-1">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="$emit('page-change', page)"
            :class="[
              'btn btn-sm',
              page === currentPage ? 'btn-primary' : 'btn-ghost'
            ]"
          >
            {{ page }}
          </button>
        </div>
        
        <span class="sm:hidden text-sm text-gray-600 dark:text-gray-400">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        
        <button
          @click="$emit('page-change', currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="btn btn-secondary btn-sm"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { TableColumn } from '../types'

interface Props {
  items: any[]
  columns: TableColumn[]
  loading?: boolean
  selectable?: boolean
  selectedItems?: any[]
  searchable?: boolean
  searchPlaceholder?: string
  exportable?: boolean
  exportFormats?: string[]
  creatable?: boolean
  createButtonText?: string
  editable?: boolean
  deletable?: boolean
  paginated?: boolean
  currentPage?: number
  pageSize?: number
  total?: number
  totalPages?: number
  ordering?: string
  emptyText?: string
  showToolbar?: boolean
  showActions?: boolean
  rowKey?: string | ((item: any) => string | number)
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  selectable: false,
  selectedItems: () => [],
  searchable: true,
  searchPlaceholder: 'Search...',
  exportable: true,
  exportFormats: () => ['csv', 'json', 'xlsx'],
  creatable: true,
  createButtonText: 'Create New',
  editable: true,
  deletable: true,
  paginated: true,
  currentPage: 1,
  pageSize: 20,
  total: 0,
  totalPages: 1,
  ordering: '',
  emptyText: 'No data available',
  showToolbar: true,
  showActions: true,
  rowKey: 'id'
})

const emit = defineEmits<{
  'search': [query: string]
  'sort': [field: string]
  'page-change': [page: number]
  'select': [items: any[]]
  'row-click': [item: any]
  'create': []
  'edit': [item: any]
  'delete': [item: any]
  'export': [format: string]
  'bulk-action': [items: any[]]
}>()

const searchQuery = ref('')
const selectedItemsLocal = ref<any[]>([])

const visibleColumns = computed(() => props.columns.filter(col => col.visible !== false))

const totalColumns = computed(() => {
  let count = visibleColumns.value.length
  if (props.selectable) count++
  if (props.showActions) count++
  return count
})

const hasSelection = computed(() => selectedItemsLocal.value.length > 0)

const allSelected = computed(() => 
  props.items.length > 0 && selectedItemsLocal.value.length === props.items.length
)

const paginationInfo = computed(() => {
  const start = (props.currentPage - 1) * props.pageSize + 1
  const end = Math.min(props.currentPage * props.pageSize, props.total)
  return { start, end }
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  const halfVisible = Math.floor(maxVisible / 2)
  
  let start = Math.max(1, props.currentPage - halfVisible)
  let end = Math.min(props.totalPages, start + maxVisible - 1)
  
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

function getItemKey(item: any): string | number {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(item)
  }
  return item[props.rowKey]
}

function getItemValue(item: any, column: TableColumn): any {
  const keys = column.key.split('.')
  return keys.reduce((obj, key) => obj?.[key], item)
}

function formatValue(value: any, column: TableColumn): string {
  if (column.format) {
    return column.format(value)
  }
  
  if (value === null || value === undefined) {
    return '-'
  }
  
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No'
  }
  
  if (value instanceof Date) {
    return value.toLocaleDateString()
  }
  
  return String(value)
}

function handleSearch() {
  emit('search', searchQuery.value)
}

function handleSort(field: string) {
  emit('sort', field)
}

function handleExport(event: Event) {
  const format = (event.target as HTMLSelectElement).value
  if (format) {
    emit('export', format)
    ;(event.target as HTMLSelectElement).value = ''
  }
}

function handleRowClick(item: any) {
  emit('row-click', item)
}

function isSelected(item: any): boolean {
  const key = getItemKey(item)
  return selectedItemsLocal.value.some(selected => getItemKey(selected) === key)
}

function toggleSelect(item: any) {
  const index = selectedItemsLocal.value.findIndex(
    selected => getItemKey(selected) === getItemKey(item)
  )
  
  if (index > -1) {
    selectedItemsLocal.value.splice(index, 1)
  } else {
    selectedItemsLocal.value.push(item)
  }
  
  emit('select', selectedItemsLocal.value)
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedItemsLocal.value = []
  } else {
    selectedItemsLocal.value = [...props.items]
  }
  
  emit('select', selectedItemsLocal.value)
}

watch(() => props.selectedItems, (newVal) => {
  selectedItemsLocal.value = newVal
}, { immediate: true })
</script>