<template>
  <form @submit.prevent="handleSubmit" class="w-full">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <svg class="spinner w-8 h-8" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
    
    <!-- Error Alert -->
    <div v-else-if="error" class="alert alert-danger mb-6">
      {{ error }}
    </div>
    
    <!-- Form Fields -->
    <div v-else class="space-y-6">
      <div
        v-for="field in visibleFields"
        :key="field.name"
        :class="getFieldClass(field)"
      >
        <label 
          :for="`field-${field.name}`" 
          class="form-label"
        >
          {{ field.label || field.name }}
          <span v-if="field.required" class="text-red-500 ml-1">*</span>
        </label>
        
        <div class="mt-1">
          <!-- Checkbox -->
          <div v-if="field.type === 'BooleanField'" class="flex items-center">
            <input
              :id="`field-${field.name}`"
              v-model="formData[field.name]"
              type="checkbox"
              class="form-checkbox"
              :required="field.required"
              :disabled="field.disabled"
              @change="handleFieldChange(field.name, $event)"
            />
            <label :for="`field-${field.name}`" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
              {{ field.help_text || field.label || field.name }}
            </label>
          </div>
          
          <!-- Select -->
          <select
            v-else-if="field.choices && field.choices.length"
            :id="`field-${field.name}`"
            v-model="formData[field.name]"
            class="form-select"
            :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500': errors[field.name] && touched.has(field.name) }"
            :required="field.required"
            :disabled="field.disabled"
            @change="handleFieldChange(field.name, $event)"
          >
            <option value="" :disabled="field.required">Select...</option>
            <option 
              v-for="choice in field.choices" 
              :key="choice.value" 
              :value="choice.value"
            >
              {{ choice.label }}
            </option>
          </select>
          
          <!-- Textarea -->
          <textarea
            v-else-if="field.type === 'TextField'"
            :id="`field-${field.name}`"
            v-model="formData[field.name]"
            class="form-textarea"
            :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500': errors[field.name] && touched.has(field.name) }"
            :placeholder="field.placeholder || field.label"
            :required="field.required"
            :disabled="field.disabled"
            :readonly="field.readonly"
            :maxlength="field.max_length"
            :minlength="field.min_length"
            @input="handleFieldChange(field.name, $event)"
          />
          
          <!-- Input -->
          <input
            v-else
            :id="`field-${field.name}`"
            v-model="formData[field.name]"
            :type="getInputType(field)"
            class="form-input"
            :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500': errors[field.name] && touched.has(field.name) }"
            :placeholder="field.placeholder || field.label"
            :required="field.required"
            :disabled="field.disabled"
            :readonly="field.readonly"
            :maxlength="field.max_length"
            :minlength="field.min_length"
            :max="field.max_value"
            :min="field.min_value"
            :step="getInputStep(field)"
            @input="handleFieldChange(field.name, $event)"
          />
          
          <!-- Help Text -->
          <p v-if="field.help_text && field.type !== 'BooleanField'" class="form-helper">
            {{ field.help_text }}
          </p>
          
          <!-- Error Message -->
          <p v-if="errors[field.name] && touched.has(field.name)" class="form-error">
            {{ errors[field.name] }}
          </p>
        </div>
      </div>
    </div>
    
    <!-- Form Actions -->
    <div class="flex items-center justify-end gap-3 mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
      <slot name="actions">
        <button
          type="button"
          @click="handleCancel"
          class="btn btn-secondary"
        >
          Cancel
        </button>
        
        <button
          type="submit"
          :disabled="!isValid || submitting"
          class="btn btn-primary"
        >
          <svg v-if="submitting" class="spinner w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ submitting ? 'Saving...' : submitText }}
        </button>
      </slot>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { FieldMetadata } from '../types'

interface Props {
  fields: FieldMetadata[]
  initialData?: Record<string, any>
  submitText?: string
  loading?: boolean
  error?: string | null
  validation?: Record<string, (value: any) => string | undefined>
  layout?: 'vertical' | 'horizontal' | 'inline'
}

const props = withDefaults(defineProps<Props>(), {
  initialData: () => ({}),
  submitText: 'Submit',
  loading: false,
  error: null,
  validation: () => ({}),
  layout: 'vertical'
})

const emit = defineEmits<{
  'submit': [data: Record<string, any>]
  'cancel': []
  'change': [field: string, value: any]
}>()

const formData = ref<Record<string, any>>({})
const errors = ref<Record<string, string>>({})
const submitting = ref(false)
const touched = ref<Set<string>>(new Set())

const visibleFields = computed(() => 
  props.fields.filter(field => field.visible !== false)
)

const isValid = computed(() => {
  for (const field of visibleFields.value) {
    if (field.required && !formData.value[field.name]) {
      return false
    }
    if (errors.value[field.name]) {
      return false
    }
  }
  return true
})

function initializeForm() {
  const data: Record<string, any> = {}
  
  for (const field of props.fields) {
    if (props.initialData[field.name] !== undefined) {
      data[field.name] = props.initialData[field.name]
    } else if (field.default !== undefined) {
      data[field.name] = field.default
    } else {
      data[field.name] = getDefaultValue(field)
    }
  }
  
  formData.value = data
}

function getDefaultValue(field: FieldMetadata): any {
  switch (field.type) {
    case 'BooleanField':
      return false
    case 'IntegerField':
    case 'DecimalField':
    case 'FloatField':
      return null
    case 'JSONField':
      return {}
    case 'ArrayField':
      return []
    default:
      return ''
  }
}

function getInputType(field: FieldMetadata): string {
  switch (field.type) {
    case 'EmailField':
      return 'email'
    case 'URLField':
      return 'url'
    case 'DateField':
      return 'date'
    case 'DateTimeField':
      return 'datetime-local'
    case 'TimeField':
      return 'time'
    case 'IntegerField':
    case 'DecimalField':
    case 'FloatField':
      return 'number'
    case 'FileField':
    case 'ImageField':
      return 'file'
    case 'PasswordField':
      return 'password'
    default:
      return 'text'
  }
}

function getInputStep(field: FieldMetadata): string | undefined {
  if (field.type === 'DecimalField') return '0.01'
  if (field.type === 'FloatField') return 'any'
  return undefined
}

function validateField(name: string, value: any): string | undefined {
  const field = props.fields.find(f => f.name === name)
  if (!field) return
  
  if (field.required && !value) {
    return `${field.label || name} is required`
  }
  
  if (props.validation[name]) {
    return props.validation[name](value)
  }
  
  if (field.type === 'EmailField' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      return 'Invalid email address'
    }
  }
  
  if (field.type === 'URLField' && value) {
    try {
      new URL(value)
    } catch {
      return 'Invalid URL'
    }
  }
  
  if ((field.type === 'CharField' || field.type === 'TextField') && value) {
    if (field.max_length && value.length > field.max_length) {
      return `Maximum length is ${field.max_length} characters`
    }
    if (field.min_length && value.length < field.min_length) {
      return `Minimum length is ${field.min_length} characters`
    }
  }
  
  if ((field.type === 'IntegerField' || field.type === 'DecimalField' || field.type === 'FloatField') && value !== null) {
    const num = Number(value)
    if (isNaN(num)) {
      return 'Must be a number'
    }
    if (field.max_value !== undefined && num > field.max_value) {
      return `Maximum value is ${field.max_value}`
    }
    if (field.min_value !== undefined && num < field.min_value) {
      return `Minimum value is ${field.min_value}`
    }
  }
}

function handleFieldChange(name: string, event: Event | any) {
  touched.value.add(name)
  
  const value = event?.target?.value ?? event
  formData.value[name] = value
  
  const error = validateField(name, value)
  if (error) {
    errors.value[name] = error
  } else {
    delete errors.value[name]
  }
  
  emit('change', name, value)
}

async function handleSubmit() {
  touched.value = new Set(visibleFields.value.map(f => f.name))
  
  const newErrors: Record<string, string> = {}
  for (const field of visibleFields.value) {
    const error = validateField(field.name, formData.value[field.name])
    if (error) {
      newErrors[field.name] = error
    }
  }
  
  errors.value = newErrors
  
  if (Object.keys(newErrors).length === 0) {
    submitting.value = true
    try {
      emit('submit', formData.value)
    } finally {
      submitting.value = false
    }
  }
}

function handleCancel() {
  emit('cancel')
}

function getFieldClass(field: FieldMetadata) {
  const classes = []
  
  if (props.layout === 'horizontal') {
    classes.push('flex', 'items-start', 'gap-4')
  } else if (props.layout === 'inline') {
    classes.push('flex', 'items-center', 'gap-4')
  }
  
  return classes
}

watch(() => props.initialData, () => {
  initializeForm()
}, { immediate: true, deep: true })
</script>