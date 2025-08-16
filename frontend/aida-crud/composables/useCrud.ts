import { ref, reactive, computed, watch } from 'vue'
import axios, { AxiosInstance } from 'axios'
import { CrudOptions, CrudState, FilterParams, BulkOperation } from '../types'

export function useCrud<T = any>(endpoint: string, options: CrudOptions = {}) {
  const state = reactive<CrudState<T>>({
    items: [],
    selectedItems: [],
    currentItem: null,
    loading: false,
    error: null,
    metadata: null,
    pagination: {
      page: 1,
      pageSize: options.pageSize || 20,
      total: 0,
      totalPages: 0
    },
    filters: {},
    search: '',
    ordering: options.defaultOrdering || '-created_at'
  })

  const api: AxiosInstance = options.api || axios.create({
    baseURL: options.baseURL || '/api',
    headers: options.headers || {}
  })

  const hasSelection = computed(() => state.selectedItems.length > 0)
  const allSelected = computed(() => 
    state.items.length > 0 && state.selectedItems.length === state.items.length
  )

  async function fetchMetadata() {
    try {
      const response = await api.options(`${endpoint}/metadata/`)
      state.metadata = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch metadata:', error)
      state.error = error
    }
  }

  async function fetchItems(params: FilterParams = {}) {
    state.loading = true
    state.error = null

    try {
      const queryParams = {
        page: state.pagination.page,
        page_size: state.pagination.pageSize,
        search: state.search || undefined,
        ordering: state.ordering || undefined,
        ...state.filters,
        ...params
      }

      const response = await api.get(endpoint, { params: queryParams })
      
      state.items = response.data.results || response.data
      
      if (response.data.count !== undefined) {
        state.pagination.total = response.data.count
        state.pagination.totalPages = Math.ceil(response.data.count / state.pagination.pageSize)
      }

      return response.data
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function getItem(id: string | number) {
    state.loading = true
    state.error = null

    try {
      const response = await api.get(`${endpoint}/${id}/`)
      state.currentItem = response.data
      return response.data
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function createItem(data: Partial<T>) {
    state.loading = true
    state.error = null

    try {
      const response = await api.post(endpoint, data)
      await fetchItems()
      return response.data
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function updateItem(id: string | number, data: Partial<T>) {
    state.loading = true
    state.error = null

    try {
      const response = await api.patch(`${endpoint}/${id}/`, data)
      await fetchItems()
      return response.data
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function deleteItem(id: string | number, hard = false) {
    state.loading = true
    state.error = null

    try {
      const url = hard ? `${endpoint}/${id}/hard-delete/` : `${endpoint}/${id}/`
      await api.delete(url)
      await fetchItems()
      return true
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function bulkCreate(items: Partial<T>[]) {
    state.loading = true
    state.error = null

    try {
      const response = await api.post(`${endpoint}/bulk-create/`, items)
      await fetchItems()
      return response.data
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function bulkUpdate(updates: Array<{ id: string | number } & Partial<T>>) {
    state.loading = true
    state.error = null

    try {
      const response = await api.patch(`${endpoint}/bulk-update/`, updates)
      await fetchItems()
      return response.data
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function bulkDelete(ids: (string | number)[]) {
    state.loading = true
    state.error = null

    try {
      await api.post(`${endpoint}/bulk-delete/`, { ids })
      await fetchItems()
      state.selectedItems = []
      return true
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function bulkAction(action: string, ids: (string | number)[], params = {}) {
    state.loading = true
    state.error = null

    try {
      const response = await api.post(`${endpoint}/bulk-action/`, {
        action,
        ids,
        params
      })
      await fetchItems()
      state.selectedItems = []
      return response.data
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function restoreItem(id: string | number) {
    state.loading = true
    state.error = null

    try {
      const response = await api.post(`${endpoint}/${id}/restore/`)
      await fetchItems()
      return response.data
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  async function exportData(format = 'csv', fields?: string[]) {
    state.loading = true
    state.error = null

    try {
      const params = {
        format,
        fields: fields?.join(','),
        ...state.filters,
        search: state.search || undefined,
        ordering: state.ordering || undefined
      }

      const response = await api.get(`${endpoint}/export/`, {
        params,
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `export.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      return true
    } catch (error) {
      state.error = error
      throw error
    } finally {
      state.loading = false
    }
  }

  function setFilter(key: string, value: any) {
    if (value === null || value === undefined || value === '') {
      delete state.filters[key]
    } else {
      state.filters[key] = value
    }
    state.pagination.page = 1
    return fetchItems()
  }

  function clearFilters() {
    state.filters = {}
    state.search = ''
    state.pagination.page = 1
    return fetchItems()
  }

  function setSearch(query: string) {
    state.search = query
    state.pagination.page = 1
    return fetchItems()
  }

  function setOrdering(field: string) {
    if (state.ordering === field) {
      state.ordering = `-${field}`
    } else if (state.ordering === `-${field}`) {
      state.ordering = ''
    } else {
      state.ordering = field
    }
    return fetchItems()
  }

  function setPage(page: number) {
    state.pagination.page = page
    return fetchItems()
  }

  function setPageSize(size: number) {
    state.pagination.pageSize = size
    state.pagination.page = 1
    return fetchItems()
  }

  function selectItem(item: T) {
    const index = state.selectedItems.indexOf(item)
    if (index > -1) {
      state.selectedItems.splice(index, 1)
    } else {
      state.selectedItems.push(item)
    }
  }

  function selectAll() {
    if (allSelected.value) {
      state.selectedItems = []
    } else {
      state.selectedItems = [...state.items]
    }
  }

  function clearSelection() {
    state.selectedItems = []
  }

  if (options.autoFetch !== false) {
    fetchMetadata()
    fetchItems()
  }

  return {
    state,
    hasSelection,
    allSelected,
    fetchMetadata,
    fetchItems,
    getItem,
    createItem,
    updateItem,
    deleteItem,
    bulkCreate,
    bulkUpdate,
    bulkDelete,
    bulkAction,
    restoreItem,
    exportData,
    setFilter,
    clearFilters,
    setSearch,
    setOrdering,
    setPage,
    setPageSize,
    selectItem,
    selectAll,
    clearSelection
  }
}