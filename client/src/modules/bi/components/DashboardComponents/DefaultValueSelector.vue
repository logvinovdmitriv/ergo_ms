<template>
  <div class="default-value-selector">
    <div class="selector-container">
      <button class="selector-button" @click="toggleDropdown" :class="{ 'open': isDropdownOpen }">
        <span class="selected-values-text">
          {{ selectedValuesText }}
        </span>
        <ChevronDown size="14" class="dropdown-arrow" />
      </button>
    </div>
    
    <div v-if="isDropdownOpen" class="modal-container">
      <div class="modal-content" @click.stop>
        <div class="search-container">
          <input v-model="searchQuery" type="text" placeholder="Поиск" class="search-input" @input="filterValues"/>
        </div>
        
        <div class="tabs-container">
          <button class="tab-btn" :class="{ 'active': activeTab === 'all' }" @click="setActiveTab('all')">Все</button>
          <button class="tab-btn" :class="{ 'active': activeTab === 'selected' }" @click="setActiveTab('selected')" v-if="props.multipleSelection">Выбранные</button>
          <button class="clear-btn" @click="clearAll" v-if="selectedValues.length > 0 && props.multipleSelection">Очистить</button>
        </div>
        
        <div class="values-list">
          <div v-for="value in displayedValues" :key="value" class="value-item" :class="{ 'selected': selectedValues.includes(value) }" @click="toggleValue(value)">
            <div class="checkbox-wrapper">
              <input type="checkbox" :checked="selectedValues.includes(value)" @change="toggleValue(value)" class="value-checkbox"/>
            </div>
            <span class="value-text">{{ value }}</span>
          </div>
          
          <div v-if="displayedValues.length === 0" class="no-values">
            <span>{{ activeTab === 'selected' ? 'Нет выбранных значений' : 'Значения не найдены' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { ChevronDown } from 'lucide-vue-next';
import datasetService from '../../js/datasetService.js';

const props = defineProps({
  datasetId: {
    type: [String, Number],
    required: true
  },
  fieldId: {
    type: [String, Number],
    required: true
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: 'Выберите значения по умолчанию'
  },
  multipleSelection: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['update:modelValue', 'mounted']);

const isDropdownOpen = ref(false);
const availableValues = ref([]);
const filteredValues = ref([]);
const searchQuery = ref('');
const isLoading = ref(false);
const error = ref('');
const activeTab = ref('all');

const selectedValues = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const selectedValuesText = computed(() => {
  if (selectedValues.value.length === 0) {
    return props.placeholder;
  }
  if (selectedValues.value.length === 1) {
    return selectedValues.value[0];
  }
  if (!props.multipleSelection) {
    return selectedValues.value[0] || props.placeholder;
  }
  return `${selectedValues.value.length} значений выбрано`;
});

const displayedValues = computed(() => {
  let baseValues = activeTab.value === 'selected' ? selectedValues.value : filteredValues.value;
  return baseValues;
});

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value;
  if (isDropdownOpen.value && availableValues.value.length === 0) {
    loadFieldValues();
  }
}

function setActiveTab(tab) {
  activeTab.value = tab;
}

function toggleValue(value) {
  const index = selectedValues.value.indexOf(value);
  if (index > -1) {
    selectedValues.value = selectedValues.value.filter(v => v !== value);
  } else {
    if (props.multipleSelection) {
      selectedValues.value = [...selectedValues.value, value];
    } else {
      selectedValues.value = [value];
      isDropdownOpen.value = false;
    }
  }
}

function clearAll() {
  selectedValues.value = [];
}

function filterValues() {
  if (!searchQuery.value) {
    filteredValues.value = availableValues.value;
  } else {
    filteredValues.value = availableValues.value.filter(value =>
      value.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }
}

async function loadFieldValues() {
  if (!props.datasetId || !props.fieldId) {
    return;
  }

  const datasetId = Number(props.datasetId);
  const fieldId = Number(props.fieldId);
  
  if (isNaN(datasetId) || isNaN(fieldId)) {
    error.value = 'Некорректные параметры запроса';
    return;
  }

  try {
    isLoading.value = true;
    error.value = '';
    const response = await datasetService.getFieldValues(datasetId, fieldId);
    availableValues.value = response.data.values || [];
    filteredValues.value = availableValues.value;
  } catch (err) {
    error.value = 'Ошибка загрузки значений поля';
    availableValues.value = [];
    filteredValues.value = [];
  } finally {
    isLoading.value = false;
  }
}

function handleClickOutside(event) {
  const modal = event.target.closest('.modal-content');
  const selector = event.target.closest('.default-value-selector');
  if (!modal && !selector) {
    isDropdownOpen.value = false;
  }
}

function handleKeyDown(event) {
  if (event.key === 'Escape') {
    isDropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  document.addEventListener('keydown', handleKeyDown);
  
  if (props.datasetId && props.fieldId) {
    loadFieldValues();
  }
  
  emit('mounted');
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  document.removeEventListener('keydown', handleKeyDown);
});

watch([() => props.datasetId, () => props.fieldId], () => {
  if (isDropdownOpen.value) {
    loadFieldValues();
  }
});

watch(() => props.multipleSelection, (newValue) => {
  if (!newValue && activeTab.value === 'selected') {
    activeTab.value = 'all';
  }
  
  if (!newValue && selectedValues.value.length > 1) {
    selectedValues.value = [selectedValues.value[0]];
  }
});
</script>

<style scoped>
.default-value-selector {
  position: relative;
  width: 100%;
}

.selector-container {
  position: relative;
  width: 100%;
}

.selector-button {
  width: 100%;
  height: 31px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--color-primary);
  }
  
  &.open {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }
}

.selected-values-text {
  flex: 1;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  color: var(--color-text-secondary, #6b7280);
  transition: transform 0.2s ease;
  flex-shrink: 0;
  
  .open & {
    transform: rotate(180deg);
  }
}

.modal-container {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  z-index: 1000;
  pointer-events: none;
}

.modal-content {
  background: var(--color-background);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  width: 335px;
  height: 314px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  z-index: 1001;
  pointer-events: auto;
  border: 1px solid var(--color-border);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-header-background);
}

.search-container {
  padding: 12px;
  border-bottom: 1px solid var(--color-border);
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 13px;
  background: var(--color-background);
  color: var(--color-text-primary);
  
  &:focus {
    outline: none;
    border-color: var(--bs-primary-border-subtle);
  }
  
  &::placeholder {
    color: var(--color-text-secondary);
  }
}

.tabs-container {
  display: flex;
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border);
  gap: 4px;
}

.tab-btn {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    color: var(--color-text-primary);
    background: var(--color-hover-background);
  }
  
  &.active {
    background: var(--color-hover-background);
    color: var(--color-text-primary);
  }
}

.clear-btn {
  margin-left: auto;
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--color-accent);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bs-primary-border-subtle);
    color: white;
  }
}

.values-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.value-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  color: var(--color-text-primary);
  
  &:hover {
    background: var(--color-hover-background);
  }
  
  &.selected {
    background: var(--color-hover-background);
    color: white;
  }
}

.checkbox-wrapper {
  flex-shrink: 0;
}

.value-checkbox {
  margin: 0;
  cursor: pointer;
  accent-color: var(--color-accent);
}

.value-text {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-values {
  padding: 20px 12px;
  text-align: center;
  color: #a0aec0;
  font-size: 13px;
}
</style> 