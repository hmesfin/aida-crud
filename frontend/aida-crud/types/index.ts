export interface CrudOptions {
  baseURL?: string
  api?: any
  headers?: Record<string, string>
  pageSize?: number
  defaultOrdering?: string
  autoFetch?: boolean
}

export interface CrudState<T> {
  items: T[]
  selectedItems: T[]
  currentItem: T | null
  loading: boolean
  error: any
  metadata: any
  pagination: Pagination
  filters: Record<string, any>
  search: string
  ordering: string
}

export interface Pagination {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

export interface FilterParams {
  [key: string]: any
}

export interface BulkOperation {
  action: string
  ids: (string | number)[]
  params?: Record<string, any>
}

export interface FieldMetadata {
  name: string
  type: string
  required: boolean
  editable: boolean
  label: string
  help_text?: string
  choices?: Array<{ value: any; label: string }>
  max_length?: number
  min_length?: number
  max_value?: number
  min_value?: number
}

export interface TableColumn {
  key: string
  label: string
  sortable?: boolean
  filterable?: boolean
  type?: string
  format?: (value: any) => string
  width?: string | number
  align?: 'left' | 'center' | 'right'
}