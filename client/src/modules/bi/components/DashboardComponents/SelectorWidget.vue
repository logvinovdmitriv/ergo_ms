<template>
  <div class="selector-widget" ref="selectorWidgetRef" :class="{ 'auto-height': effectiveAutoHeight }">
    <div class="selector-content">
      <div v-if="isLoading" class="selector-loading">
        <Loader2 class="spinner" :size="24" />
        <span>Загрузка селектора...</span>
      </div>

      <div v-else-if="error" class="selector-error">
        <AlertCircle :size="24" />
        <span>{{ error }}</span>
      </div>

      <div v-else class="selector-render-container">
        <!-- ОТОБРАЖЕНИЕ ВСЕХ СЕЛЕКТОРОВ ПОСТРОЧНО -->
        <div class="selectors-list-container">
          <div v-for="(selector, index) in sortedSelectors" 
               :key="selector.id" 
               class="selector-row" 
               :class="{ 'favorite': selector.isFavorite }">
            
            <!-- Рендер отдельного селектора -->
            <div class="selector-list" :class="getSelectorLayoutClasses(selector)">
              <label v-if="selector?.titlePosition !== 'hidden'" class="selector-label">
                {{ selector?.title || 'Селектор' }}
                <div v-if="selector?.showHint && selector?.hintText" 
                     class="hint-icon-wrapper" 
                     @mouseenter="showHint($event, selector)" 
                     @mouseleave="hideHint"
                     @click.stop>
                  <HelpCircle :size="16" />
                </div>
              </label>
              
              <select v-if="!selector?.selectorType || selector?.selectorType === 'list'" 
                      class="selector-dropdown" 
                      :value="getSelectorValue(selector)" 
                      @change="handleSelectionChange(selector, $event)"
                      :class="{ 
                        'with-internal-title': selector?.showInternalTitle && selector?.internalTitle,
                        'with-color-accent': selector?.showColorAccent 
                      }">
                <option value="">{{ getPlaceholderText(selector) }}</option>
                <option v-if="getSelectorOptions(selector).length === 0 && !selector?.selectedDatasetId" 
                        value="" disabled>Настройте датасет и поле</option> -->
                <option v-for="option in getSelectorOptions(selector)" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              
              <!-- Дата -->
              <input v-else-if="selector?.selectorType === 'date'" 
                     type="date" 
                     :value="getSelectorValue(selector)" 
                     @change="handleSelectionChange(selector, $event)" 
                     class="date-input"
                     :class="{ 
                       'with-internal-title': selector?.showInternalTitle && selector?.internalTitle,
                       'with-color-accent': selector?.showColorAccent 
                     }"
                     :title="selector?.showInternalTitle && selector?.internalTitle ? selector.internalTitle : ''" />
              
              <!-- Диапазон -->
              <div v-else-if="selector?.selectorType === 'range'" class="range-container">
                <input type="range" 
                       :value="getSelectorValue(selector)" 
                       :min="selector?.rangeMin || 0" 
                       :max="selector?.rangeMax || 100" 
                       :step="selector?.rangeStep || 1"
                       @input="handleSelectionChange(selector, $event)" 
                       class="range-input" />
                <span class="range-value">{{ getSelectorValue(selector) }}</span>
              </div>
              
              <!-- Радиокнопки -->
              <div v-else-if="selector?.selectorType === 'radio'" class="radio-group">
                <label v-for="option in getSelectorOptions(selector)" :key="option.value" class="radio-item">
                  <input type="radio" 
                         :value="option.value" 
                         :checked="getSelectorValue(selector) === option.value"
                         @change="handleSelectionChange(selector, $event)" />
                  <span class="radio-label">{{ option.label }}</span>
                </label>
              </div>
              
              <!-- Чекбоксы -->
              <div v-else-if="selector?.selectorType === 'checkbox'" class="checkbox-group">
                <label v-for="option in getSelectorOptions(selector)" :key="option.value" class="checkbox-item">
                  <input type="checkbox" 
                         :value="option.value" 
                         :checked="getSelectedValues(selector).includes(option.value)"
                         @change="handleMultiSelectionChange(selector, $event)" />
                  <span class="checkbox-label">{{ option.label }}</span>
                </label>
              </div>
              
              <!-- Поле ввода (input) -->
              <input v-else-if="selector?.selectorType === 'input'" 
                     type="text" 
                     :value="getSelectorValue(selector)" 
                     @input="handleInputChange(selector, $event)" 
                     class="selector-input"
                     :class="{ 
                       'with-internal-title': selector?.showInternalTitle && selector?.internalTitle,
                       'with-color-accent': selector?.showColorAccent 
                     }"
                     :placeholder="getPlaceholderText(selector)" />
            </div>
          </div>
        </div>
        
        <!-- Кнопки управления фильтрами - вынесены вниз -->
        <div v-if="selectorGroupSettings?.applyButton || selectorGroupSettings?.clearButton" class="selector-actions">
          <button v-if="selectorGroupSettings?.applyButton" 
                  class="btn-apply" 
                  @click="applyFilters">
            Применить
          </button>
          <button v-if="selectorGroupSettings?.clearButton" 
                  class="btn-clear" 
                  @click="clearFilters">
            Сбросить
          </button>
        </div>

      </div>
    </div>

    <!-- Тултип подсказки -->
    <Teleport to="body">
      <div v-if="hintVisible"
           class="hint-tooltip" 
           :style="hintTooltipStyle"
           @mouseenter="cancelHideHint"
           @mouseleave="hideHint">
        <div v-html="hintContent" class="hint-content"></div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { Loader2, AlertCircle, Filter, ChevronDown, HelpCircle } from 'lucide-vue-next';
import datasetService from '../../js/datasetService.js';

const props = defineProps({
  selectorsList: {
    type: Array,
    default: () => []
  },
  activeSelectorIndex: {
    type: Number,
    default: 0
  },
  autoHeight: {
    type: Boolean,
    default: false
  },
  selectorGroupSettings: {
    type: Object,
    default: () => ({
      applyButton: false,
      clearButton: false,
      autoHeight: false
    })
  }
});

const emit = defineEmits(['selection-change', 'content-resized', 'apply-filters', 'clear-filters']);

const isLoading = ref(false);
const error = ref('');
const isDropdownOpen = ref(false);
const selectedValue = ref('');
const selectedValues = ref([]);
const selectorWidgetRef = ref(null);
const selectorValues = ref({});
const selectorOptionsMap = ref({});
const selectorLoadingStates = ref({});
const calculatedHeight = ref(null);

const hintVisible = ref(false);
const hintContent = ref('');
const hintTooltipStyle = ref({});
let hideHintTimer = null;

const currentSelector = computed(() => {
  const selector = props.selectorsList?.[props.activeSelectorIndex] || null;
  
  if (selector) {
    try {
      const reactiveSelector = JSON.parse(JSON.stringify(selector));
      return reactiveSelector;
    } catch (e) {
      console.error('Failed to make reactive:', e);
      return selector;
    }
  }
  
  return selector;
});

const effectiveAutoHeight = computed(() => {
  return props.autoHeight || props.selectorGroupSettings?.autoHeight || false;
});

const sortedSelectors = computed(() => {
  if (!props.selectorsList || props.selectorsList.length === 0) return [];
  
  const sorted = [...props.selectorsList].sort((a, b) => {
    if (a.isFavorite && !b.isFavorite) return -1;
    if (!a.isFavorite && b.isFavorite) return 1;
    
    return (a.id || 0) - (b.id || 0);
  });
  
  sorted.forEach(selector => {
    if (!selectorValues.value.hasOwnProperty(selector.id)) {
      if (selector.selectorType === 'checkbox') {
        selectorValues.value[selector.id] = Array.isArray(selector.defaultValue) ? selector.defaultValue : [];
      } else if (selector.selectorType === 'input') {
        selectorValues.value[selector.id] = '';
      } else {
        selectorValues.value[selector.id] = selector.defaultValue || '';
      }
    }
    
    if (!selectorOptionsMap.value.hasOwnProperty(selector.id) && 
        selector.selectedDatasetId && 
        selector.selectedField) {
      loadSelectorOptions(selector);
    }
  });
  
  return sorted;
});



const selectedLabel = computed(() => {
  if (!currentSelector.value) return '';
  const options = getSelectorOptions(currentSelector.value);
  const option = options.find(opt => opt.value === selectedValue.value);
  return option ? option.label : '';
});

const rangeMin = computed(() => {
  return currentSelector.value?.rangeMin || 0;
});

const rangeMax = computed(() => {
  return currentSelector.value?.rangeMax || 100;
});

const rangeStep = computed(() => {
  return currentSelector.value?.rangeStep || 1;
});

function shouldShowTitle() {
  return currentSelector.value?.titlePosition !== 'hidden';
}

function getDisplayTitle() {
  return currentSelector.value?.title || 'Селектор';
}

function getPlaceholderText(selector = null) {
  const selectorData = selector || currentSelector.value;
  if (selectorData?.showInternalTitle && selectorData?.internalTitle) {
    return selectorData.internalTitle;
  }
  return getDefaultValueText(selectorData) || 'Выберите значение';
}

function getSelectorOptions(selector) {
  if (!selector || !selector.id) return [];
  return selectorOptionsMap.value[selector.id] || [];
}

async function loadSelectorOptions(selector) {
  if (!selector || !selector.selectedDatasetId || !selector.selectedField) {
    selectorOptionsMap.value[selector.id] = [];
    return;
  }
  
  selectorLoadingStates.value[selector.id] = true;
  
  try {
    const response = await datasetService.getFieldValues(selector.selectedDatasetId, selector.selectedField);
    const options = response.data ? response.data.map(value => ({
      value: value,
      label: value
    })) : [];
    
    selectorOptionsMap.value[selector.id] = options;
  } catch (error) {
    console.error('Ошибка загрузки опций селектора:', error);
    selectorOptionsMap.value[selector.id] = [];
  } finally {
    selectorLoadingStates.value[selector.id] = false;
  }
}

function getSelectorValue(selector) {
  return selectorValues.value[selector.id] || '';
}

function setSelectorValue(selector, value) {
  selectorValues.value[selector.id] = value;
}

function getSelectedValues(selector) {
  const value = selectorValues.value[selector.id];
  return Array.isArray(value) ? value : [];
}

function setSelectedValues(selector, values) {
  selectorValues.value[selector.id] = values;
}

function getTitleClasses() {
  const classes = [];
  if (currentSelector.value?.titlePosition === 'left') {
    classes.push('title-left');
  } else if (currentSelector.value?.titlePosition === 'top') {
    classes.push('title-top');
  }
  return classes;
}

function getSelectorLayoutClasses(selector = null) {
  const selectorData = selector || currentSelector.value;
  const classes = [];
  
  if (selectorData?.titlePosition === 'left') {
    classes.push('title-position-left');
  } else if (selectorData?.titlePosition === 'top') {
    classes.push('title-position-top');
  }
  
  if (selectorData?.showColorAccent) {
    classes.push('with-color-accent');
  }
  
  return classes;
}

function getSelectorClasses() {
  const classes = [];
  if (currentSelector.value?.showColorAccent) {
    classes.push('with-color-accent');
  }
  if (currentSelector.value?.titlePosition === 'left') {
    classes.push('title-position-left');
  } else if (currentSelector.value?.titlePosition === 'top') {
    classes.push('title-position-top');
  }
  return classes;
}

function getDefaultValueText(selector = null) {
  const selectorData = selector || currentSelector.value;
  if (!selectorData?.defaultValue) return '';

  if (Array.isArray(selectorData.defaultValue)) {
    if (selectorData.defaultValue.length === 0) return '';
    if (selectorData.defaultValue.length === 1) {
      return selectorData.defaultValue[0];
    }
    return selectorData.defaultValue.join(', ');
  }

  return selectorData.defaultValue || '';
}

function showHint(event, selector = null) {
  const selectorData = selector || currentSelector.value;
  if (!selectorData?.hintText) return;
  
  const rect = event.target.getBoundingClientRect();
  hintContent.value = selectorData.hintText;
  hintTooltipStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 8}px`,
    left: `${rect.left}px`,
    zIndex: '10000'
  };
  hintVisible.value = true;
  
  if (hideHintTimer) {
    clearTimeout(hideHintTimer);
    hideHintTimer = null;
  }
}

function hideHint() {
  hideHintTimer = setTimeout(() => {
    hintVisible.value = false;
  }, 100);
}

function cancelHideHint() {
  if (hideHintTimer) {
    clearTimeout(hideHintTimer);
    hideHintTimer = null;
  }
}

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value;
}

function selectOption(option) {
  selectedValue.value = option.value;
  isDropdownOpen.value = false;
  handleSelectionChange();
}

function handleSelectionChange(selector = null, event = null) {
  if (selector && event) {
    const newValue = event.target.value;
    setSelectorValue(selector, newValue);
    
    emit('selection-change', {
      selectorId: selector.id,
      value: newValue,
      type: 'single'
    });
  } else {
    emit('selection-change', {
      selectorId: currentSelector.value?.id,
      value: selectedValue.value,
      type: 'single'
    });
  }
}

function handleMultiSelectionChange(selector, event) {
  if (!selector || !event) {
    emit('selection-change', {
      selectorId: currentSelector.value?.id,
      value: selectedValues.value,
      type: 'multiple'
    });
    return;
  }
  
  const newValue = event.target.value;
  const isChecked = event.target.checked;
  const currentValues = getSelectedValues(selector);
  
  let updatedValues;
  if (isChecked) {
    updatedValues = [...currentValues, newValue];
  } else {
    updatedValues = currentValues.filter(val => val !== newValue);
  }
  
  setSelectedValues(selector, updatedValues);
  
  emit('selection-change', {
    selectorId: selector.id,
    value: updatedValues,
    type: 'multiple'
  });
}

function handleInputChange(selector, event) {
  const newValue = event.target.value;
  setSelectorValue(selector, newValue);
  
  emit('selection-change', {
    selectorId: selector.id,
    value: newValue,
    type: 'input'
  });
}

function applyFilters() {
  emit('apply-filters', {
    selectorId: currentSelector.value?.id,
    value: selectedValue.value
  });
}

function clearFilters() {
  selectedValue.value = '';
  selectedValues.value = [];
  emit('clear-filters', {
    selectorId: currentSelector.value?.id
  });
}

watch(() => props.selectorsList, (newList, oldList) => {
  if (!newList) return;
  
  newList.forEach(selector => {
    const oldSelector = oldList?.find(old => old.id === selector.id);
    
    if (!oldSelector || 
        oldSelector.selectedDatasetId !== selector.selectedDatasetId ||
        oldSelector.selectedField !== selector.selectedField) {
      if (selector.selectedDatasetId && selector.selectedField) {
        loadSelectorOptions(selector);
      }
    }
    
    if (oldSelector && oldSelector.selectorType !== selector.selectorType) {
      if (selector.selectorType === 'checkbox') {
        selectorValues.value[selector.id] = [];
      } else {
        selectorValues.value[selector.id] = '';
      }
    }
    
    if (selector.selectorType === 'input' && selectorValues.value[selector.id]) {
      const currentValue = selectorValues.value[selector.id];
      if (typeof currentValue === 'string' && /^[\d.]+$/.test(currentValue.trim())) {
        selectorValues.value[selector.id] = '';
      }
    }
  });
}, { deep: true });

function calculateWidgetHeight() {
  if (!effectiveAutoHeight.value || !selectorWidgetRef.value) return;

  nextTick(() => {
    const element = selectorWidgetRef.value;
    if (element) {
      element.style.height = 'auto';

      nextTick(() => {
        const selectorContent = element.querySelector('.selector-content');
        if (selectorContent) {
          const contentHeight = selectorContent.scrollHeight;
          
          const computedStyle = window.getComputedStyle(element);
          const paddingTop = parseFloat(computedStyle.paddingTop);
          const paddingBottom = parseFloat(computedStyle.paddingBottom);
          const borderTop = parseFloat(computedStyle.borderTopWidth);
          const borderBottom = parseFloat(computedStyle.borderBottomWidth);
          
          let newHeight = contentHeight + paddingTop + paddingBottom + borderTop + borderBottom;
          
          newHeight = Math.max(newHeight, 50);

          if (calculatedHeight.value !== newHeight) {
            calculatedHeight.value = newHeight;
            emit('content-resized', newHeight);
          }
        }
      });
    }
  });
}

function triggerHeightRecalculation() {
  if (effectiveAutoHeight.value) {
    calculateWidgetHeight();
  }
}

function handleClickOutside(event) {
  if (!selectorWidgetRef.value?.contains(event.target)) {
    isDropdownOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);

  if (effectiveAutoHeight.value) {
    calculateWidgetHeight();
  }
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  if (hideHintTimer) {
    clearTimeout(hideHintTimer);
  }
});

watch(() => props.selectorsList, () => {
  if (effectiveAutoHeight.value) {
    nextTick(() => {
      calculateWidgetHeight();
    });
  }
}, { deep: true });

watch(() => currentSelector.value, () => {
  if (effectiveAutoHeight.value) {
    nextTick(() => {
      calculateWidgetHeight();
    });
  }
}, { deep: true });

watch(() => props.selectorGroupSettings?.autoHeight, (newValue) => {
  if (newValue) {
    nextTick(() => {
      calculateWidgetHeight();
    });
  }
});

watch(() => props.activeSelectorIndex, () => {
  if (effectiveAutoHeight.value) {
    nextTick(() => {
      calculateWidgetHeight();
    });
  }
});

defineExpose({
  triggerHeightRecalculation
});
</script>

<style scoped lang="scss">
.selector-widget {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  padding: 3px;
  box-sizing: border-box;

  &.auto-height {
    height: auto !important;
    min-height: 50px;
    
    .selector-content {
      height: auto !important;
      min-height: auto;
    }
    
    .selector-render-container {
      height: auto !important;
      min-height: auto;
    }
    
    .selector-list {
      height: auto !important;
      min-height: auto;
    }
  }
}

.selector-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 12px;
}

.selector-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--color-text-secondary);
  font-size: 14px;
  height: 100%;

  .spinner {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.selector-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--color-accent);
  font-size: 14px;
  height: 100%;
}

.selector-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--color-text-secondary);
  font-size: 14px;
  height: 100%;
  text-align: center;
}

.selector-render-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
  width: 100%;
}

.selector-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;

  &.title-left {
    margin-bottom: 0;
    margin-right: 8px;
  }

  &.title-top {
    margin-bottom: 8px;
  }
}

.hint-icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: help;
  color: var(--color-text-secondary);
  transition: color 0.2s ease;
  
  &:hover {
    color: var(--color-accent);
  }
}

.selector-list,
.selector-dropdown-container,
.selector-radio,
.selector-checkbox,
.selector-date,
.selector-range,
.selector-default {
  display: flex;
  flex-direction: column;
  gap: 8px;
  height: 100%;
  width: 100%;
  &.title-position-left {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 8px;

    .selector-label {
      flex-shrink: 0;
      margin-bottom: 0;
    }

    .selector-dropdown,
    .custom-dropdown,
    .radio-group,
    .checkbox-group,
    .date-input,
    .range-container {
      flex: 1;
    }
  }
  
  &.title-position-top {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .selector-label {
      margin-bottom: 4px;
    }
  }

  &.with-color-accent {
    border: 2px solid var(--color-accent);
    border-radius: 6px;
    padding: 8px;
    background: rgba(var(--color-accent-rgb), 0.05);
    
    .selector-dropdown,
    .dropdown-button,
    .date-input {
      border-color: var(--color-accent);
      background: rgba(var(--color-accent-rgb), 0.1);
      
      &:focus {
        border-color: var(--color-accent);
        box-shadow: 0 0 0 2px rgba(var(--color-accent-rgb), 0.2);
      }
      
      &.with-internal-title {
        background: rgba(var(--color-accent-rgb), 0.15);
        
        &::placeholder {
          color: var(--color-accent);
          font-weight: 500;
        }
      }
    }
  }
}

.selector-dropdown {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text-primary);
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: var(--color-primary);
  }
  
  &.with-color-accent {
    border-color: var(--color-primary);
    background: rgba(var(--color-primary-rgb), 0.05);
  }
}

.custom-dropdown {
  position: relative;
  width: 100%;
}

.dropdown-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text-primary);
  font-size: 14px;
  cursor: pointer;

  &:hover {
    border-color: var(--color-primary);
  }
}

.dropdown-icon {
  transition: transform 0.2s ease;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.dropdown-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-primary);

  &:hover {
    background: var(--color-hover-background);
  }

  &.selected {
    background: var(--color-primary-background);
    color: white;
  }
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-primary);

  input[type="radio"] {
    accent-color: var(--color-primary);
  }
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-primary);

  input[type="checkbox"] {
    accent-color: var(--color-primary);
  }
}

.date-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text-primary);
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: var(--color-primary);
  }
}

.range-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.range-input {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--color-border);
  outline: none;
  cursor: pointer;

  &::-webkit-slider-thumb {
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--color-primary);
    cursor: pointer;
  }

  &::-moz-range-thumb {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--color-primary);
    cursor: pointer;
    border: none;
  }
}

.range-value {
  font-size: 14px;
  color: var(--color-text-primary);
  min-width: 40px;
  text-align: center;
}

.hint-tooltip {
  position: fixed;
  background: var(--color-background);
  color: var(--color-text-primary);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 400;
  white-space: normal;
  z-index: 10000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--color-border);
  max-width: 250px;
  min-width: 150px;
  width: max-content;
  word-wrap: break-word;
  
  &::after {
    content: '';
    position: absolute;
    top: -6px;
    left: 20px;
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-bottom: 6px solid var(--color-background);
    filter: drop-shadow(0 -1px 0 var(--color-border));
  }
}

.hint-content {
  line-height: 1.4;
}

.selector-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  justify-content: flex-start;
  width: 100%;
  
  .btn-apply,
  .btn-clear {
    padding: 6px 16px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
  }
  
  .btn-apply {
    background: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
    
    &:hover {
      background: var(--color-primary-hover, var(--color-primary));
      filter: brightness(1.1);
    }
    
    &:active {
      transform: translateY(1px);
    }
  }
  
  .btn-clear {
    background: var(--color-background);
    color: var(--color-text-secondary);
    border-color: var(--color-border);
    
    &:hover {
      background: var(--color-hover-background);
      border-color: var(--color-primary);
      color: var(--color-text-primary);
    }
    
    &:active {
      transform: translateY(1px);
    }
  }
}

.selectors-list-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  height: 100%;
}

.selector-row {
  width: 100%;
  
  &.favorite {
    order: -1;
    
    .selector-label {
      font-weight: 600;
      color: var(--color-primary);
      
      &::before {
        content: '★ ';
        color: var(--color-primary);
        font-size: 14px;
      }
    }
  }
}

.selector-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text-primary);
  font-size: 14px;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.2);
  }

  &.with-color-accent {
    border-color: var(--color-primary);
    background: rgba(var(--color-primary-rgb), 0.05);
  }

  &.with-internal-title {
    font-style: italic;
    
    &:not(:focus) {
      background: var(--color-background-muted);
    }
  }
}

.selector-dropdown.with-internal-title,
.dropdown-button.with-internal-title,
.date-input.with-internal-title {
  font-style: italic;
  
  &:not(:focus) {
    background: var(--color-background-muted);
  }
}




</style>