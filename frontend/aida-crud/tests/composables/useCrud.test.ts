import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useCrud } from '../../composables/useCrud'
import axios from 'axios'

vi.mock('axios')

describe('useCrud', () => {
  const mockEndpoint = '/api/test'
  const mockData = [
    { id: 1, name: 'Item 1' },
    { id: 2, name: 'Item 2' },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('initialization', () => {
    it('should initialize with default state', () => {
      const { state } = useCrud(mockEndpoint, { autoFetch: false })

      expect(state.items).toEqual([])
      expect(state.selectedItems).toEqual([])
      expect(state.currentItem).toBeNull()
      expect(state.loading).toBe(false)
      expect(state.error).toBeNull()
      expect(state.search).toBe('')
      expect(state.pagination.page).toBe(1)
      expect(state.pagination.pageSize).toBe(20)
    })

    it('should auto-fetch on initialization when autoFetch is true', async () => {
      const mockApi = {
        options: vi.fn().mockResolvedValue({ data: {} }),
        get: vi.fn().mockResolvedValue({ data: { results: mockData, count: 2 } }),
      }

      const { state } = useCrud(mockEndpoint, { api: mockApi })

      await vi.waitFor(() => {
        expect(mockApi.options).toHaveBeenCalledWith(`${mockEndpoint}/metadata/`)
        expect(mockApi.get).toHaveBeenCalledWith(mockEndpoint, expect.any(Object))
      })
    })
  })

  describe('CRUD operations', () => {
    let crud: ReturnType<typeof useCrud>
    let mockApi: any

    beforeEach(() => {
      mockApi = {
        get: vi.fn(),
        post: vi.fn(),
        patch: vi.fn(),
        delete: vi.fn(),
        options: vi.fn().mockResolvedValue({ data: {} }),
      }
      crud = useCrud(mockEndpoint, { api: mockApi, autoFetch: false })
    })

    it('should fetch items', async () => {
      mockApi.get.mockResolvedValue({
        data: { results: mockData, count: 2 },
      })

      await crud.fetchItems()

      expect(mockApi.get).toHaveBeenCalledWith(mockEndpoint, {
        params: {
          page: 1,
          page_size: 20,
          search: undefined,
          ordering: '-created_at',
        },
      })
      expect(crud.state.items).toEqual(mockData)
      expect(crud.state.pagination.total).toBe(2)
    })

    it('should get single item', async () => {
      const item = mockData[0]
      mockApi.get.mockResolvedValue({ data: item })

      const result = await crud.getItem(1)

      expect(mockApi.get).toHaveBeenCalledWith(`${mockEndpoint}/1/`)
      expect(result).toEqual(item)
      expect(crud.state.currentItem).toEqual(item)
    })

    it('should create item', async () => {
      const newItem = { name: 'New Item' }
      const createdItem = { id: 3, ...newItem }
      
      mockApi.post.mockResolvedValue({ data: createdItem })
      mockApi.get.mockResolvedValue({ data: { results: [], count: 0 } })

      const result = await crud.createItem(newItem)

      expect(mockApi.post).toHaveBeenCalledWith(mockEndpoint, newItem)
      expect(result).toEqual(createdItem)
    })

    it('should update item', async () => {
      const updates = { name: 'Updated' }
      const updatedItem = { id: 1, ...updates }
      
      mockApi.patch.mockResolvedValue({ data: updatedItem })
      mockApi.get.mockResolvedValue({ data: { results: [], count: 0 } })

      const result = await crud.updateItem(1, updates)

      expect(mockApi.patch).toHaveBeenCalledWith(`${mockEndpoint}/1/`, updates)
      expect(result).toEqual(updatedItem)
    })

    it('should delete item', async () => {
      mockApi.delete.mockResolvedValue({})
      mockApi.get.mockResolvedValue({ data: { results: [], count: 0 } })

      const result = await crud.deleteItem(1)

      expect(mockApi.delete).toHaveBeenCalledWith(`${mockEndpoint}/1/`)
      expect(result).toBe(true)
    })

    it('should hard delete item', async () => {
      mockApi.delete.mockResolvedValue({})
      mockApi.get.mockResolvedValue({ data: { results: [], count: 0 } })

      await crud.deleteItem(1, true)

      expect(mockApi.delete).toHaveBeenCalledWith(`${mockEndpoint}/1/hard-delete/`)
    })
  })

  describe('bulk operations', () => {
    let crud: ReturnType<typeof useCrud>
    let mockApi: any

    beforeEach(() => {
      mockApi = {
        get: vi.fn().mockResolvedValue({ data: { results: [], count: 0 } }),
        post: vi.fn(),
        patch: vi.fn(),
        options: vi.fn().mockResolvedValue({ data: {} }),
      }
      crud = useCrud(mockEndpoint, { api: mockApi, autoFetch: false })
    })

    it('should bulk create items', async () => {
      const items = [{ name: 'Item 1' }, { name: 'Item 2' }]
      mockApi.post.mockResolvedValue({ data: items })

      await crud.bulkCreate(items)

      expect(mockApi.post).toHaveBeenCalledWith(`${mockEndpoint}/bulk-create/`, items)
    })

    it('should bulk update items', async () => {
      const updates = [
        { id: 1, name: 'Updated 1' },
        { id: 2, name: 'Updated 2' },
      ]
      mockApi.patch.mockResolvedValue({ data: updates })

      await crud.bulkUpdate(updates)

      expect(mockApi.patch).toHaveBeenCalledWith(`${mockEndpoint}/bulk-update/`, updates)
    })

    it('should bulk delete items', async () => {
      const ids = [1, 2, 3]
      mockApi.post.mockResolvedValue({})

      await crud.bulkDelete(ids)

      expect(mockApi.post).toHaveBeenCalledWith(`${mockEndpoint}/bulk-delete/`, { ids })
      expect(crud.state.selectedItems).toEqual([])
    })

    it('should perform bulk action', async () => {
      const ids = [1, 2]
      const action = 'archive'
      const params = { reason: 'test' }
      
      mockApi.post.mockResolvedValue({ data: { archived: 2 } })

      const result = await crud.bulkAction(action, ids, params)

      expect(mockApi.post).toHaveBeenCalledWith(`${mockEndpoint}/bulk-action/`, {
        action,
        ids,
        params,
      })
      expect(result).toEqual({ archived: 2 })
    })
  })

  describe('filtering and search', () => {
    let crud: ReturnType<typeof useCrud>
    let mockApi: any

    beforeEach(() => {
      mockApi = {
        get: vi.fn().mockResolvedValue({ data: { results: [], count: 0 } }),
        options: vi.fn().mockResolvedValue({ data: {} }),
      }
      crud = useCrud(mockEndpoint, { api: mockApi, autoFetch: false })
    })

    it('should set filter', async () => {
      await crud.setFilter('status', 'active')

      expect(crud.state.filters.status).toBe('active')
      expect(crud.state.pagination.page).toBe(1)
    })

    it('should remove filter when value is null', async () => {
      crud.state.filters.status = 'active'
      
      await crud.setFilter('status', null)

      expect(crud.state.filters.status).toBeUndefined()
    })

    it('should clear all filters', async () => {
      crud.state.filters = { status: 'active', type: 'basic' }
      crud.state.search = 'test'

      await crud.clearFilters()

      expect(crud.state.filters).toEqual({})
      expect(crud.state.search).toBe('')
      expect(crud.state.pagination.page).toBe(1)
    })

    it('should set search query', async () => {
      await crud.setSearch('test query')

      expect(crud.state.search).toBe('test query')
      expect(crud.state.pagination.page).toBe(1)
    })

    it('should toggle ordering', async () => {
      crud.state.ordering = ''
      
      await crud.setOrdering('name')
      expect(crud.state.ordering).toBe('name')

      await crud.setOrdering('name')
      expect(crud.state.ordering).toBe('-name')

      await crud.setOrdering('name')
      expect(crud.state.ordering).toBe('')
    })
  })

  describe('pagination', () => {
    let crud: ReturnType<typeof useCrud>
    let mockApi: any

    beforeEach(() => {
      mockApi = {
        get: vi.fn().mockResolvedValue({ data: { results: [], count: 0 } }),
        options: vi.fn().mockResolvedValue({ data: {} }),
      }
      crud = useCrud(mockEndpoint, { api: mockApi, autoFetch: false })
    })

    it('should set page', async () => {
      await crud.setPage(3)

      expect(crud.state.pagination.page).toBe(3)
      expect(mockApi.get).toHaveBeenCalledWith(
        mockEndpoint,
        expect.objectContaining({
          params: expect.objectContaining({ page: 3 }),
        })
      )
    })

    it('should set page size', async () => {
      await crud.setPageSize(50)

      expect(crud.state.pagination.pageSize).toBe(50)
      expect(crud.state.pagination.page).toBe(1)
    })
  })

  describe('selection', () => {
    let crud: ReturnType<typeof useCrud>

    beforeEach(() => {
      const mockApi = {
        get: vi.fn().mockResolvedValue({ data: { results: mockData, count: 2 } }),
        options: vi.fn().mockResolvedValue({ data: {} }),
      }
      crud = useCrud(mockEndpoint, { api: mockApi, autoFetch: false })
      crud.state.items = mockData
    })

    it('should select item', () => {
      const item = mockData[0]
      
      crud.selectItem(item)
      expect(crud.state.selectedItems).toContain(item)

      crud.selectItem(item)
      expect(crud.state.selectedItems).not.toContain(item)
    })

    it('should select all items', () => {
      crud.selectAll()
      expect(crud.state.selectedItems).toEqual(mockData)
      expect(crud.allSelected.value).toBe(true)
    })

    it('should clear selection', () => {
      crud.state.selectedItems = [...mockData]
      
      crud.clearSelection()
      expect(crud.state.selectedItems).toEqual([])
      expect(crud.hasSelection.value).toBe(false)
    })
  })
})