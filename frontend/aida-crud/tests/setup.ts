import { config } from '@vue/test-utils'

// Global test setup
config.global.mocks = {
  $t: (key: string) => key, // Mock i18n if needed
}

// Mock window.URL.createObjectURL for export tests
global.URL.createObjectURL = vi.fn(() => 'mock-url')
global.URL.revokeObjectURL = vi.fn()

// Mock document methods for export tests
Object.defineProperty(document.body, 'appendChild', {
  value: vi.fn(),
})

Object.defineProperty(document.body, 'removeChild', {
  value: vi.fn(),
})