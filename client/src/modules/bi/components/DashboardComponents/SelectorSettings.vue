<template>
  <div class="widget-settings">
    <div class="widget-settings-left-side">
      <h5 class="widget-settings-left-side-title">Селекторы</h5>
      <div class="selectors-list">
        <transition-group name="selector-list" tag="div" class="selectors-container">
          <div v-for="(selector, index) in selectorsList" :key="selector.id" class="selector-item" :class="{ 
              active: activeSelectorIndex === index,
              dragging: draggedIndex === index,
              'drag-over': dragOverIndex === index && draggedIndex !== index
            }"
            draggable="true"
            @dragstart="handleDragStart(index, $event)"
            @dragover.prevent="handleDragOver(index, $event)"
            @drop="handleDrop(index, $event)"
            @dragenter.prevent="handleDragEnter(index, $event)"
            @dragleave="handleDragLeave($event)"
            @dragend="handleDragEnd"
            @click="setActiveSelector(index)">
            <span class="selector-icon">
              <GripVertical absoluteStrokeWidth size="14" class="drag-handle"/>
              <Star size="20" :class="{ 
                  'star-favorite': selector.isFavorite,
                  'star-regular': !selector.isFavorite
                }" @click.stop="toggleFavorite(index)"/>
            </span>
            <span class="selector-name" :title="selector.title">{{ selector.title }}</span>
            <button v-if="selectorsList.length > 1" class="delete-selector-btn" @click.stop="removeSelector(index)" title="Удалить селектор">✕</button>
          </div>
        </transition-group>
        <button class="add-selector-btn" @click="addNewSelector"><span class="plus-icon">➕</span>Добавить селектор</button>
      </div>
      <button class="advanced-settings-btn" @click="openAdvancedSettings">
        <Settings size="16" class="settings-icon" />
        Расширенные настройки
      </button>
    </div>
    <div class="widget-settings-right-side">
      <div class="widget-settings-right-side-header">
        <h5 class="widget-settings-right-side-title">Настройки селектора</h5>
        <button class="close-btn" @click="onCancel" title="Закрыть">
          <span class="close-icon">×</span>
        </button>
      </div>
      <div class="widget-settings-right-side-content">
        <div class="settings-table">
          <div class="settings-section">
            <h6 class="section-title">Данные</h6>
            
            <div class="settings-row">
              <div class="settings-label">Источник</div>
              <div class="settings-control">
                <div class="source-selector">
                  <div class="input-group">
                    <div class="input-wrapper">
                      <div v-if="currentSelector.sourceType === 'dataset' && currentSelector.selectedDataset" class="input-icon-wrapper">
                        <Database class="input-icon" />
                      </div>
                      <div v-if="currentSelector.sourceType === 'url' && currentSelector.datasetUrl" class="input-icon-wrapper">
                        <Link class="input-icon" />
                      </div>
                      <input 
                        v-model="sourceInputValue"
                        type="text" 
                        class="form-control-button"
                        style="border-top-right-radius: 0px !important;  border-bottom-right-radius: 0px !important;"
                        :placeholder="sourceInputPlaceholder"
                        @click="handleSourceInputClick"
                        @input="handleSourceInputChange"
                        :readonly="currentSelector.sourceType === 'dataset'"
                        :class="['form-control', { 
                          'source-select-mode': currentSelector.sourceType === 'dataset',
                          'has-icon': (currentSelector.sourceType === 'dataset' && currentSelector.selectedDataset) || (currentSelector.sourceType === 'url' && currentSelector.datasetUrl),
                          'source-url-error': currentSelector.sourceType === 'url' && urlValidationResult && !urlValidationResult.isValid,
                          'source-url-success': currentSelector.sourceType === 'url' && urlValidationResult && urlValidationResult.isValid
                        }]"
                      />
                    </div>
                    <button 
                      :class="['btn btn-outline-secondary dropdown-toggle', {
                        'source-url-error': currentSelector.sourceType === 'url' && urlValidationResult && !urlValidationResult.isValid,
                        'source-url-success': currentSelector.sourceType === 'url' && urlValidationResult && urlValidationResult.isValid
                      }]"
                      @click.stop="toggleDropdown"
                      type="button"
                      :aria-expanded="isDropdownOpen"
                    >
                      {{ currentSelector.sourceType === 'dataset' ? 'Датасет' : 'URL' }}
                    </button>
                    <ul v-if="isDropdownOpen" class="dropdown-menu">
                      <li>
                        <a class="dropdown-item" @click.stop="selectSourceType('dataset')" :class="{ active: currentSelector.sourceType === 'dataset' }">
                          Датасет
                        </a>
                      </li>
                      <li>
                        <a class="dropdown-item" @click.stop="selectSourceType('url')" :class="{ active: currentSelector.sourceType === 'url' }">
                          URL
                        </a>
                      </li>
                    </ul>
                  </div>
                </div>
                
                <div v-if="currentSelector.sourceType === 'url' && (isUrlValidating || urlValidationResult)" class="url-validation-result">
                  <div v-if="isUrlValidating" class="validation-loading">
                    <span class="loading-spinner"></span>
                    <span class="loading-text">Проверка URL...</span>
                  </div>
                  <div v-else-if="urlValidationResult" :class="['validation-message', urlValidationResult.isValid ? 'success-message' : 'error-message']">
                    <span class="validation-icon">
                      <CheckCircle v-if="urlValidationResult.isValid" size="16" />
                      <CircleAlert v-else size="16" />
                    </span>
                    <div class="validation-content">
                      <span class="validation-text">{{ urlValidationResult.message }}</span>
                      <div v-if="urlValidationResult.isValid && urlValidationResult.datasetName" class="dataset-info">
                        <strong>Датасет:</strong> {{ urlValidationResult.datasetName }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="settings-row" v-if="currentSelector.sourceType === 'dataset' && currentSelector.selectedDataset">
              <div class="settings-label">Поле</div>
              <div class="settings-control">
                <div class="field-selector-container">
                  <div class="custom-field-select">
                    <button class="field-select-button" @click="toggleFieldDropdown" :class="{ 'open': isFieldDropdownOpen }">
                      <FieldTypeIcon 
                        v-if="selectedFieldType"
                        :field-type="selectedFieldType"
                        :size="14"
                        class="selected-field-icon"
                      />
                      <span class="field-select-text">
                        {{ selectedFieldName || 'Выберите поле' }}
                      </span>
                      <ChevronDown size="14" class="dropdown-arrow" />
                    </button>
                    <div v-if="isFieldDropdownOpen" class="field-dropdown-menu">
                      <div 
                        v-for="field in availableFields" 
                        :key="field.id"
                        class="field-dropdown-item"
                        :class="{ 'selected': currentSelector.selectedField === field.id }"
                        @click="selectField(field.id)"
                      >
                        <FieldTypeIcon 
                          :field-type="field.type"
                          :size="14"
                          class="field-icon"
                        />
                        <span class="field-name">{{ field.name }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="settings-row" v-if="currentSelector.sourceType === 'url' && urlValidationResult && urlValidationResult.isValid && currentSelector.selectedDatasetId">
              <div class="settings-label">Поле</div>
              <div class="settings-control">
                <div class="field-selector-container">
                  <div class="custom-field-select">
                    <button class="field-select-button" @click="toggleFieldDropdown" :class="{ 'open': isFieldDropdownOpen }">
                      <FieldTypeIcon 
                        v-if="selectedFieldType"
                        :field-type="selectedFieldType"
                        :size="14"
                        class="selected-field-icon"
                      />
                      <span class="field-select-text">
                        {{ selectedFieldName || 'Выберите поле' }}
                      </span>
                      <ChevronDown size="14" class="dropdown-arrow" />
                    </button>
                    <div v-if="isFieldDropdownOpen" class="field-dropdown-menu">
                      <div 
                        v-for="field in availableFields" 
                        :key="field.id"
                        class="field-dropdown-item"
                        :class="{ 'selected': currentSelector.selectedField === field.id }"
                        @click="selectField(field.id)"
                      >
                        <FieldTypeIcon 
                          :field-type="field.type"
                          :size="14"
                          class="field-icon"
                        />
                        <span class="field-name">{{ field.name }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="settings-section">
            <h6 class="section-title">Фильтрация</h6>
            
            <div class="settings-row">
              <div class="settings-label">Тип селектора</div>
              <div class="settings-control">
                <div class="selector-type-dropdown">
                  <button class="selector-type-toggle" @click="toggleSelectorTypeDropdown" :class="{ 'open': isSelectorTypeDropdownOpen }">
                    <span class="selector-type-icon">
                      <List v-if="currentSelector.selectorType === 'list'" size="16" />
                      <Type v-else-if="currentSelector.selectorType === 'input'" size="16" />
                      <Calendar v-else-if="currentSelector.selectorType === 'calendar'" size="16" />
                      <CheckSquare v-else-if="currentSelector.selectorType === 'checkbox'" size="16" />
                      <ChevronDown v-else size="16" />
                    </span>
                    <span class="selector-type-text">
                      {{ getSelectorTypeLabel(currentSelector.selectorType) }}
                    </span>
                    <ChevronDown size="14" class="dropdown-arrow" />
                  </button>
                  <div v-if="isSelectorTypeDropdownOpen" class="selector-type-menu">
                    <div 
                      v-for="type in selectorTypesWithAvailability" 
                      :key="type.value"
                      class="selector-type-option"
                      :class="{ 
                        'active': currentSelector.selectorType === type.value,
                        'disabled': !type.isAvailable
                      }"
                      @click="type.isAvailable ? selectSelectorType(type.value) : null"
                      :title="!type.isAvailable ? type.disabledReason : ''"
                    >
                      <span class="selector-type-icon">
                        <List v-if="type.value === 'list'" size="16" />
                        <Type v-else-if="type.value === 'input'" size="16" />
                        <Calendar v-else-if="type.value === 'calendar'" size="16" />
                        <CheckSquare v-else-if="type.value === 'checkbox'" size="16" />
                      </span>
                      <span class="selector-type-text">{{ type.label }}</span>
                      <span v-if="!type.isAvailable" class="disabled-indicator">
                        <Info size="12" />
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="settings-row">
              <div class="settings-label">
                Операция
              </div>
              <div class="settings-control">
                <div class="operation-dropdown">
                  <button class="operation-toggle" @click="toggleOperationDropdown" :class="{ 'open': isOperationDropdownOpen }">
                    <span class="operation-text">
                      {{ currentOperationLabel }}
                    </span>
                    <ChevronDown size="14" class="dropdown-arrow" />
                  </button>
                  <div v-if="isOperationDropdownOpen" class="operation-menu">
                    <div 
                      v-for="operation in availableOperations" 
                      :key="operation.value"
                      class="operation-option"
                      :class="{ 'active': currentSelector.operation === operation.value }"
                      @click="selectOperation(operation.value)"
                    >
                      <span class="operation-text">{{ operation.label }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="settings-row" v-if="currentSelector.selectorType === 'list'">
              <div class="settings-label">
                <input type="checkbox" v-model="currentSelector.multipleSelection" />
                Множественный выбор
              </div>
            </div>
            
            <div class="settings-row">
              <div class="settings-label">Значение по умолчанию</div>
              <div class="settings-control">
                <!-- Показываем DefaultValueSelector для списков -->
                <div v-if="shouldShowDefaultValueSelector && currentSelector.selectorType === 'list'" class="default-value-selector-container">
                  <DefaultValueSelector
                    :dataset-id="Number(currentSelector.selectedDatasetId)"
                    :field-id="Number(currentSelector.selectedField)"
                    v-model="currentSelector.defaultValue"
                    :multiple-selection="currentSelector.multipleSelection"
                    :placeholder="currentSelector.required ? 'Выберите значения по умолчанию (обязательно)' : 'Выберите значения по умолчанию'"
                    :class="{ 'is-invalid': currentSelector.required && (!currentSelector.defaultValue || currentSelector.defaultValue.length === 0) }"
                  />
                  <div v-if="currentSelector.required && (!currentSelector.defaultValue || currentSelector.defaultValue.length === 0)" class="invalid-feedback">
                    Это поле обязательно для заполнения
                  </div>
                </div>
                <!-- Показываем обычный инпут для поля ввода -->
                <div v-else-if="currentSelector.selectorType === 'input'" class="default-input-container">
                  <input 
                    v-model="currentSelector.inputDefaultValue"
                    type="text" 
                    class="form-control input-sm"
                    placeholder="Введите значение по умолчанию"
                    :class="{ 'is-invalid': currentSelector.required && !currentSelector.inputDefaultValue }"
                  />
                  <div v-if="currentSelector.required && !currentSelector.inputDefaultValue" class="invalid-feedback">
                    Это поле обязательно для заполнения
                  </div>
                </div>
                <!-- Сообщение когда поле не выбрано -->
                <div v-else-if="!shouldShowDefaultValueSelector" class="no-field-selected">
                  <span class="text-muted">Сначала выберите поле датасета</span>
                </div>
                <!-- Для других типов селекторов пока что показываем заглушку -->
                <div v-else class="other-selector-type">
                  <span class="text-muted">Настройка значений по умолчанию для данного типа селектора пока не поддерживается</span>
                </div>
              </div>
            </div>
            
            <div class="settings-row">
              <div class="settings-label">
                <input type="checkbox" v-model="currentSelector.required" />
                Обязательное поле
              </div>
            </div>
          </div>
          
          <div class="settings-section">
            <h6 class="section-title">Отображение</h6>
            
            <div class="settings-row">
              <div class="settings-label">Заголовок</div>
              <div class="settings-control">
                <div class="input-group">
                  <input 
                    v-model="currentSelector.title" 
                    type="text" 
                    placeholder="Заголовок селектора"
                    class="form-control"
                  />
                </div>
                <div class="title-position-buttons">
                  <button 
                    class="position-btn" 
                    style="border-top-right-radius: 0px !important;  border-bottom-right-radius: 0px !important; border-right-width: 0px;"
                    :class="{ active: currentSelector.titlePosition === 'hidden' }"
                    @click="setTitlePosition('hidden')"
                  >
                    Скрыт
                  </button>
                  <button 
                    class="position-btn" 
                    style="border-radius: 0px !important; border-right-width: 0.5px;"
                    :class="{ active: currentSelector.titlePosition === 'left' }"
                    @click="setTitlePosition('left')"
                  >
                    Слева
                  </button>
                  <button 
                    class="position-btn" 
                    style="border-top-left-radius: 0px !important;  border-bottom-left-radius: 0px !important; border-left-width: 0px;"
                    :class="{ active: currentSelector.titlePosition === 'top' }"
                    @click="setTitlePosition('top')"
                  >
                    Сверху
                  </button>
                </div>
              </div>
            </div>
            
            <div class="settings-row">
              <div class="settings-label">
                <input type="checkbox" v-model="currentSelector.showInternalTitle" />Внутренний заголовок
                <div class="help-icon-wrapper">
                  <HelpCircle 
                    size="14" 
                    class="help-icon" 
                    @mouseenter="showInternalTitleTooltip = true"
                    @mouseleave="showInternalTitleTooltip = false"
                  />
                  <div v-if="showInternalTitleTooltip" class="custom-tooltip">
                    Внутренний заголовок позволяет указать текст внутри селектора. Например, его можно использовать для отображения операции внутри селектора.<br><br>Недоступен в селекторах типа «Чекбокс».
                  </div>
                </div>
              </div>
              <div class="settings-control" v-if="currentSelector.showInternalTitle">
                <input 
                  v-model="currentSelector.internalTitle" 
                  type="text" 
                  placeholder="Внутренний заголовок"
                  class="form-control"
                />
              </div>
            </div>
            
            <div class="settings-row">
              <div class="settings-label">
                <input type="checkbox" v-model="currentSelector.showColorAccent" />
                Цветовой акцент
                <div class="help-icon-wrapper">
                  <HelpCircle 
                    size="14" 
                    class="help-icon" 
                    @mouseenter="showColorAccentTooltip = true"
                    @mouseleave="showColorAccentTooltip = false"
                  />
                  <div v-if="showColorAccentTooltip" class="custom-tooltip">
                    Используйте опцию для выделения цветом важных селекторов
                  </div>
                </div>
              </div>
            </div>
            
            <div class="settings-row">
              <div class="settings-label">
                <input type="checkbox" v-model="currentSelector.showHint" />
                Подсказка
              </div>
              <div class="settings-control" v-if="currentSelector.showHint">
                <div class="text-editor-wrapper">
                  <TextEditor 
                    v-model:hintText="currentSelector.hintText"
                    :content="currentSelector.hintText"
                    @update:hintText="updateHintText"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="widget-settings-right-side-actions">
        <div v-if="!isFormValid && validationMessage" class="validation-hint" :class="{ 'clickable': invalidSelectorIndex !== activeSelectorIndex }" @click="goToInvalidSelector">
          <CircleAlert size="14" class="hint-icon" />
          <span class="hint-text">{{ validationMessage }}</span>
          <span v-if="invalidSelectorIndex !== activeSelectorIndex" class="hint-action">Нажмите для перехода</span>
        </div>
        <div class="action-buttons">
          <button @click="onCancel" class="cancel">Отменить</button>
          <button class="btn btn-primary" @click="onSubmit" :disabled="!isFormValid">Сохранить</button>
        </div>
      </div>
    </div>
    
    <div v-if="isDatasetModalOpen" class="dataset-modal-overlay" @click.self="closeDatasetModal">
      <div class="dataset-modal-container">
        <div class="dataset-modal-header">
          <h6 class="dataset-modal-title">Выбор датасета</h6>
          <button class="dataset-modal-close" @click="closeDatasetModal" title="Закрыть">
            <span class="close-icon">×</span>
          </button>
        </div>
        <div class="dataset-modal-content">
          <DatasetsTooltip
            :selected-dataset="currentSelector.selectedDataset ? { name: currentSelector.selectedDataset, id: currentSelector.selectedDatasetId } : null"
            :datasets="availableDatasets"
            :is-loading="isDatasetsLoading"
            @select="selectDataset"
          />
        </div>
      </div>
    </div>

    <!-- Модальное окно расширенных настроек -->
    <div v-if="isAdvancedSettingsModalOpen" class="advanced-settings-modal-overlay" @click.self="closeAdvancedSettings">
      <div class="advanced-settings-modal-container">
        <div class="advanced-settings-modal-header">
          <h6 class="advanced-settings-modal-title">Настройки группы селекторов</h6>
          <button class="advanced-settings-modal-close" @click="closeAdvancedSettings" title="Закрыть">
            <span class="close-icon">×</span>
          </button>
        </div>
        <div class="advanced-settings-modal-content">
          <div class="settings-section">
            <h6 class="section-title">Параметры группы</h6>
            
            <div class="setting-item">
              <label class="setting-label">
                <input 
                  type="checkbox" 
                  v-model="selectorGroupSettings.applyButton"
                  class="setting-checkbox"
                />
                Кнопка «Применить»
              </label>
              <span class="setting-hint">Добавляет кнопку для применения выбранных фильтров</span>
            </div>

            <div class="setting-item">
              <label class="setting-label">
                <input 
                  type="checkbox" 
                  v-model="selectorGroupSettings.clearButton"
                  class="setting-checkbox"
                />
                Кнопка «Сбросить»
              </label>
              <span class="setting-hint">Добавляет кнопку для сброса всех фильтров</span>
            </div>

            <div class="setting-item">
              <label class="setting-label">
                <input 
                  type="checkbox" 
                  v-model="selectorGroupSettings.autoHeight"
                  class="setting-checkbox"
                />
                Автовысота
              </label>
              <span class="setting-hint">Автоматически подстраивает высоту под содержимое</span>
            </div>
          </div>
          
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="closeAdvancedSettings">
              Отмена
            </button>
            <button class="btn btn-primary" @click="saveAdvancedSettings">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue';
import { Star, GripVertical, Settings, Database, HelpCircle, ChevronDown, Link, CheckCircle, CircleAlert, List, Type, Calendar, CheckSquare, Info } from 'lucide-vue-next';
import DatasetsTooltip from '../ChartComponents/DatasetsTooltip.vue';
import TextEditor from './TextEditor.vue';
import FieldTypeIcon from './FieldTypeIcon.vue';
import DefaultValueSelector from './DefaultValueSelector.vue';
import datasetService from '../../js/datasetService.js';
import { getFieldTypeTooltip } from './js/fieldTypeIcons.js';
import { validateDatasetUrlWithAccess } from './js/datasetUrlUtils.js';
import { apiClient } from '@/js/api/manager.js';

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['close', 'save']);

const selectorsList = ref([
  {
    id: 1,
    title: 'Селектор 1',
    titlePosition: 'left',
    showInternalTitle: false,
    internalTitle: '',
    showColorAccent: false,
    showHint: false,
    hintText: '',
    sourceType: 'dataset',
    selectedDataset: '',
    selectedDatasetId: null,
    selectedField: '',
    selectorType: 'list',
    operation: '',
    multipleSelection: false,
    defaultValue: [],
    required: false,
    isFavorite: true
  }
]);

const activeSelectorIndex = ref(0);
const draggedIndex = ref(null);
const dragOverIndex = ref(null);
const isDatasetModalOpen = ref(false);
const isAdvancedSettingsModalOpen = ref(false);
const availableDatasets = ref([]);
const availableFields = ref([]);
const selectorOptions = ref([]);
const isDatasetsLoading = ref(false);

const originalData = ref(null);

const selectorGroupSettings = ref({
  applyButton: false,
  clearButton: false,
  autoHeight: false
});

const currentSelector = computed(() => {
  return selectorsList.value[activeSelectorIndex.value] || {};
});

function validateSelector(selector, isCurrentSelector = false) {
  if (!selector.title || selector.title.trim().length === 0) {
    return false;
  }
  
  if (selector.sourceType === 'dataset') {
    if (!selector.selectedDataset || !selector.selectedDatasetId) {
      return false;
    }
  } else if (selector.sourceType === 'url') {
    if (isCurrentSelector) {
      if (!urlValidationResult.value || !urlValidationResult.value.isValid || !selector.selectedDatasetId) {
        return false;
      }
    } else {
      if (!selector.selectedDatasetId) {
        return false;
      }
    }
  }
  
  if (!selector.selectedField) {
    return false;
  }
  
  if (selector.required) {
    if (!selector.defaultValue || 
        (Array.isArray(selector.defaultValue) && selector.defaultValue.length === 0) ||
        (typeof selector.defaultValue === 'string' && selector.defaultValue.trim().length === 0)) {
      return false;
    }
  }
  
  return true;
}

const isFormValid = computed(() => {
  for (let i = 0; i < selectorsList.value.length; i++) {
    const selector = selectorsList.value[i];
    const isCurrentSelector = i === activeSelectorIndex.value;
    
    if (!validateSelector(selector, isCurrentSelector)) {
      return false;
    }
  }
  
  return true;
});

const validationMessage = computed(() => {
  for (let i = 0; i < selectorsList.value.length; i++) {
    const selector = selectorsList.value[i];
    const isCurrentSelector = i === activeSelectorIndex.value;
    const selectorNumber = i + 1;
    
    if (!selector.title || selector.title.trim().length === 0) {
      return `Селектор ${selectorNumber}: Заполните заголовок`;
    }
    
    if (selector.sourceType === 'dataset') {
      if (!selector.selectedDataset || !selector.selectedDatasetId) {
        return `Селектор ${selectorNumber}: Выберите датасет`;
      }
    } else if (selector.sourceType === 'url') {
      if (isCurrentSelector) {
        if (!urlValidationResult.value || !urlValidationResult.value.isValid) {
          return `Селектор ${selectorNumber}: Введите корректный URL датасета`;
        }
        if (!selector.selectedDatasetId) {
          return `Селектор ${selectorNumber}: Дождитесь загрузки данных датасета`;
        }
      } else {
        if (!selector.selectedDatasetId) {
          return `Селектор ${selectorNumber}: Настройте источник данных (URL)`;
        }
      }
    }
    
    if (!selector.selectedField) {
      return `Селектор ${selectorNumber}: Выберите поле датасета`;
    }
    
    if (selector.required) {
      if (!selector.defaultValue || 
          (Array.isArray(selector.defaultValue) && selector.defaultValue.length === 0) ||
          (typeof selector.defaultValue === 'string' && selector.defaultValue.trim().length === 0)) {
        return `Селектор ${selectorNumber}: Выберите значение по умолчанию (обязательный)`;
      }
    }
  }
  
  return '';
});

const invalidSelectorIndex = computed(() => {
  for (let i = 0; i < selectorsList.value.length; i++) {
    const selector = selectorsList.value[i];
    const isCurrentSelector = i === activeSelectorIndex.value;
    
    if (!validateSelector(selector, isCurrentSelector)) {
      return i;
    }
  }
  
  return -1;
});

function goToInvalidSelector() {
  if (invalidSelectorIndex.value >= 0) {
    activeSelectorIndex.value = invalidSelectorIndex.value;
  }
}

const sourceInputValue = ref('');

const sourceInputPlaceholder = computed(() => {
  if (currentSelector.value.sourceType === 'dataset') {
    return 'Выберите датасет';
  } else if (currentSelector.value.sourceType === 'url') {
    return 'Введите URL источника данных';
  }
  return '';
});

const selectedFieldType = computed(() => {
  if (!currentSelector.value.selectedField) return null;
  
  const selectedField = availableFields.value.find(field => field.id === currentSelector.value.selectedField);
  return selectedField ? selectedField.type : null;
});

const selectedFieldName = computed(() => {
  if (!currentSelector.value.selectedField) return null;
  
  const selectedField = availableFields.value.find(field => field.id === currentSelector.value.selectedField);
  return selectedField ? selectedField.name : null;
});

const shouldShowDefaultValueSelector = computed(() => {
  const hasField = currentSelector.value.selectedField && 
                   currentSelector.value.selectedField !== '' && 
                   currentSelector.value.selectedField !== null;
  const hasDataset = currentSelector.value.selectedDatasetId && 
                     currentSelector.value.selectedDatasetId !== '' && 
                     currentSelector.value.selectedDatasetId !== null;
  
  return hasField && hasDataset;
});

const isDropdownOpen = ref(false);
const isSelectorTypeDropdownOpen = ref(false);
const isFieldDropdownOpen = ref(false);
const isOperationDropdownOpen = ref(false);
const isUrlValidating = ref(false);
const urlValidationResult = ref(null);
const showColorAccentTooltip = ref(false);
const showInternalTitleTooltip = ref(false);

const selectorTypes = ref([
  { value: 'list', label: 'Список', icon: 'List' },
  { value: 'input', label: 'Поле ввода', icon: 'Type' },
  { value: 'calendar', label: 'Календарь', icon: 'Calendar' },
  { value: 'checkbox', label: 'Чекбокс', icon: 'CheckSquare' }
]);

const selectorTypesWithAvailability = computed(() => {
  const fieldType = selectedFieldType.value;
  
  return selectorTypes.value.map(selectorType => {
    let isAvailable = true;
    let disabledReason = '';
    
    if (selectorType.value === 'calendar') {
      isAvailable = fieldType === 'date&time';
      if (!isAvailable) {
        disabledReason = 'Доступно только для полей типа "Дата и время"';
      }
    }
    
    if (selectorType.value === 'checkbox') {
      isAvailable = fieldType === 'bool';
      if (!isAvailable) {
        disabledReason = 'Доступно только для полей типа "Логический"';
      }
    }
    
    return {
      ...selectorType,
      isAvailable,
      disabledReason
    };
  });
});

const availableSelectorTypes = computed(() => {
  return selectorTypesWithAvailability.value.filter(type => type.isAvailable);
});

const allOperations = ref([
  { value: 'equals', label: 'Равно', applicableTypes: ['string', 'integer', 'float', 'date', 'date&time', 'bool'] },
  { value: 'in', label: 'Принадлежит множеству', applicableTypes: ['string'] },
  { value: 'not_in', label: 'Не принадлежит множеству', applicableTypes: ['string'] },
  { value: 'contains', label: 'Содержит', applicableTypes: ['string'] },
  { value: 'starts_with', label: 'Начинается с', applicableTypes: ['string'] },
  { value: 'ends_with', label: 'Заканчивается на', applicableTypes: ['string'] },
  { value: 'greater_than', label: 'Больше', applicableTypes: ['integer', 'float', 'date', 'date&time'] },
  { value: 'less_than', label: 'Меньше', applicableTypes: ['integer', 'float', 'date', 'date&time'] },
  { value: 'between', label: 'Между', applicableTypes: ['integer', 'float', 'date', 'date&time'] },
  { value: 'greater_than_or_equal', label: 'Больше или равно', applicableTypes: ['integer', 'float', 'date', 'date&time'] },
  { value: 'less_than_or_equal', label: 'Меньше или равно', applicableTypes: ['integer', 'float', 'date', 'date&time'] },
  { value: 'is_true', label: 'Истина', applicableTypes: ['bool'] },
  { value: 'is_false', label: 'Ложь', applicableTypes: ['bool'] }
]);

const availableOperations = computed(() => {
  const fieldType = selectedFieldType.value;
  
  if (!fieldType) {
    return [];
  }
  
  return allOperations.value.filter(operation => 
    operation.applicableTypes.includes(fieldType)
  );
});

const currentOperationLabel = computed(() => {
  if (!currentSelector.value?.operation) {
    return '—';
  }
  
  const operation = allOperations.value.find(op => op.value === currentSelector.value.operation);
  return operation ? operation.label : '—';
});

function createNewSelector() {
  return {
    id: Date.now() + Math.random(),
    title: `Селектор ${selectorsList.value.length + 1}`,
    titlePosition: 'left',
    showInternalTitle: false,
    internalTitle: '',
    showColorAccent: false,
    showHint: false,
    hintText: '',
    sourceType: 'dataset',
    selectedDataset: '',
    selectedDatasetId: null,
    datasetUrl: '',
    selectedField: '',
    selectorType: 'list',
    operation: '',
    multipleSelection: false,
    defaultValue: [],
    inputDefaultValue: '',
    required: false,
    isFavorite: false
  };
}

function addNewSelector() {
  const newSelector = createNewSelector();
  selectorsList.value.push(newSelector);
  activeSelectorIndex.value = selectorsList.value.length - 1;
}

function removeSelector(index) {
  if (selectorsList.value.length <= 1) return;
  
  const wasRemovalFavorite = selectorsList.value[index].isFavorite;
  
  selectorsList.value.splice(index, 1);
  
  if (wasRemovalFavorite && selectorsList.value.length > 0) {
    selectorsList.value[0].isFavorite = true;
  }
  
  if (activeSelectorIndex.value >= selectorsList.value.length) {
    activeSelectorIndex.value = selectorsList.value.length - 1;
  } else if (activeSelectorIndex.value > index) {
    activeSelectorIndex.value--;
  }
}

function setActiveSelector(index) {
  activeSelectorIndex.value = index;
}

function handleDragStart(index, event) {
  draggedIndex.value = index;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', index.toString());
  
  setTimeout(() => {
    if (event.target) {
      event.target.style.opacity = '0.5';
    }
  }, 0);
}

function handleDragOver(index, event) {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'move';
}

function handleDragEnter(index, event) {
  event.preventDefault();
  if (draggedIndex.value !== null && draggedIndex.value !== index) {
    dragOverIndex.value = index;
  }
}

function handleDragLeave(event) {
  if (!event.currentTarget.contains(event.relatedTarget)) {
    dragOverIndex.value = null;
  }
}

function handleDrop(targetIndex, event) {
  event.preventDefault();
  
  if (draggedIndex.value === null || draggedIndex.value === targetIndex) {
    return;
  }
  
  const draggedSelector = selectorsList.value[draggedIndex.value];
  selectorsList.value.splice(draggedIndex.value, 1);
  selectorsList.value.splice(targetIndex, 0, draggedSelector);
  
  if (activeSelectorIndex.value === draggedIndex.value) {
    activeSelectorIndex.value = targetIndex;
  } else if (activeSelectorIndex.value > draggedIndex.value && activeSelectorIndex.value <= targetIndex) {
    activeSelectorIndex.value--;
  } else if (activeSelectorIndex.value < draggedIndex.value && activeSelectorIndex.value >= targetIndex) {
    activeSelectorIndex.value++;
  }
  
  draggedIndex.value = null;
  dragOverIndex.value = null;
}

function handleDragEnd(event) {
  if (event.target) {
    event.target.style.opacity = '';
  }
  draggedIndex.value = null;
  dragOverIndex.value = null;
}

function toggleFavorite(index) {
  if (selectorsList.value[index].isFavorite) {
    return;
  }
  
  selectorsList.value.forEach((selector, i) => {
    selector.isFavorite = i === index;
  });
}

function openAdvancedSettings() {
  isAdvancedSettingsModalOpen.value = true;
}

function closeAdvancedSettings() {
  isAdvancedSettingsModalOpen.value = false;
}

function saveAdvancedSettings() {
  closeAdvancedSettings();
}

function openDatasetModal() {
  isDatasetModalOpen.value = true;
  availableDatasets.value = [];
  loadAvailableDatasets();
}

function closeDatasetModal() {
  isDatasetModalOpen.value = false;
}

async function loadAvailableDatasets() {
  try {
    isDatasetsLoading.value = true;
    const response = await datasetService.getUserDatasets();
    availableDatasets.value = response.data || [];
  } catch (error) {
    availableDatasets.value = [];
  } finally {
    isDatasetsLoading.value = false;
  }
}

function selectDataset(dataset) {
  const availableDatasetIds = availableDatasets.value.map(d => d.id);
  if (!availableDatasetIds.includes(dataset.id)) {
    return;
  }
  
  currentSelector.value.selectedDataset = dataset.name;
  currentSelector.value.selectedDatasetId = dataset.id;
  currentSelector.value.sourceType = 'dataset';
  currentSelector.value.datasetUrl = '';
  currentSelector.value.selectedField = '';
  
  sourceInputValue.value = dataset.name;
  
  urlValidationResult.value = null;
  isUrlValidating.value = false;
  isDropdownOpen.value = false;
  closeDatasetModal();
  loadAvailableFields();
}

async function loadAvailableFields() {
  if (!currentSelector.value.selectedDatasetId) {
    availableFields.value = [];
    return;
  }
  
  try {
    const response = await datasetService.listFields({ dataset: currentSelector.value.selectedDatasetId });
    availableFields.value = response.data || [];
  } catch (error) {
    availableFields.value = [];
  }
}

function setTitlePosition(position) {
  currentSelector.value.titlePosition = position;
}

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value;
}

function toggleSelectorTypeDropdown() {
  isSelectorTypeDropdownOpen.value = !isSelectorTypeDropdownOpen.value;
}

function toggleFieldDropdown() {
  isFieldDropdownOpen.value = !isFieldDropdownOpen.value;
}

function toggleOperationDropdown() {
  isOperationDropdownOpen.value = !isOperationDropdownOpen.value;
}

function selectField(fieldId) {
  currentSelector.value.selectedField = fieldId;
  isFieldDropdownOpen.value = false;
}

function selectOperation(operationValue) {
  currentSelector.value.operation = operationValue;
  isOperationDropdownOpen.value = false;
}

function selectSelectorType(type) {
  const selectorType = selectorTypesWithAvailability.value.find(t => t.value === type);
  
  if (!selectorType || !selectorType.isAvailable) {
    return;
  }
  
  currentSelector.value.selectorType = type;
  isSelectorTypeDropdownOpen.value = false;
  
  if (type === 'input') {
    currentSelector.value.multipleSelection = false;
  }
}

function getSelectorTypeLabel(type) {
  const selectorType = selectorTypes.value.find(t => t.value === type);
  return selectorType ? selectorType.label : 'Выберите тип';
}

function selectSourceType(type) {
  currentSelector.value.sourceType = type;
  isDropdownOpen.value = false;
  urlValidationResult.value = null;
  isUrlValidating.value = false;
  
  if (type === 'dataset') {
    currentSelector.value.datasetUrl = '';
    currentSelector.value.selectedField = '';
  } else if (type === 'url') {
    currentSelector.value.selectedDataset = '';
    currentSelector.value.selectedDatasetId = null;
    currentSelector.value.selectedField = '';
  }
}

function handleSourceInputClick() {
  if (currentSelector.value.sourceType === 'dataset') {
    openDatasetModal();
  }
}

function handleSourceInputChange() {
  if (currentSelector.value.sourceType === 'url') {
    currentSelector.value.datasetUrl = sourceInputValue.value;
    const url = sourceInputValue.value.trim();
    if (url) {
      validateUrl(url);
    } else {
      urlValidationResult.value = null;
      isUrlValidating.value = false;
    }
  }
}

let validationTimeout = null;

function validateUrl(url) {
  if (validationTimeout) {
    clearTimeout(validationTimeout);
  }
  
  isUrlValidating.value = true;
  urlValidationResult.value = null;
  
  if (!url || !url.trim()) {
    isUrlValidating.value = false;
    return;
  }
  
  validationTimeout = setTimeout(async () => {
    try {
      const result = await validateDatasetUrlWithAccess(url.trim(), apiClient, true);
      
      urlValidationResult.value = {
        isValid: result.isValid,
        message: result.isValid ? 'URL датасета корректен!' : result.error,
        datasetId: result.datasetId,
        datasetName: result.datasetName
      };
      
      if (result.isValid) {
        currentSelector.value.selectedDatasetId = result.datasetId;
        currentSelector.value.selectedDataset = result.datasetName;
        
        if (currentSelector.value.sourceType === 'url') {
          sourceInputValue.value = currentSelector.value.datasetUrl;
        }
        
        loadAvailableFields();
      }
      
    } catch (error) {
      console.error('Ошибка при валидации URL датасета:', error);
      urlValidationResult.value = {
        isValid: false,
        message: 'Произошла ошибка при проверке URL',
        datasetId: null,
        datasetName: null
      };
    } finally {
      isUrlValidating.value = false;
    }
  }, 500);
}

function handleClickOutside(event) {
  if (!isDropdownOpen.value && !isSelectorTypeDropdownOpen.value && !isFieldDropdownOpen.value && !isOperationDropdownOpen.value) {
    return;
  }
  
  const dropdownToggle = event.target.closest('.dropdown-toggle');
  const dropdownMenu = event.target.closest('.dropdown-menu');
  const selectorTypeToggle = event.target.closest('.selector-type-toggle');
  const selectorTypeMenu = event.target.closest('.selector-type-menu');
  const fieldSelectButton = event.target.closest('.field-select-button');
  const fieldDropdownMenu = event.target.closest('.field-dropdown-menu');
  const operationToggle = event.target.closest('.operation-toggle');
  const operationMenu = event.target.closest('.operation-menu');
   
  if (dropdownToggle || dropdownMenu) {
    return;
  }
  
  if (selectorTypeToggle || selectorTypeMenu) {
    return;
  }
  
  if (fieldSelectButton || fieldDropdownMenu) {
    return;
  }
  
  if (operationToggle || operationMenu) {
    return;
  }
  
  isDropdownOpen.value = false;
  isSelectorTypeDropdownOpen.value = false;
  isFieldDropdownOpen.value = false;
  isOperationDropdownOpen.value = false;
}

function handleKeyDown(event) {
  if (event.key === 'Escape') {
    if (isAdvancedSettingsModalOpen.value) {
      isAdvancedSettingsModalOpen.value = false;
    } else if (isDatasetModalOpen.value) {
      isDatasetModalOpen.value = false;
    } else if (isDropdownOpen.value) {
      isDropdownOpen.value = false;
    } else if (isSelectorTypeDropdownOpen.value) {
      isSelectorTypeDropdownOpen.value = false;
    } else if (isFieldDropdownOpen.value) {
      isFieldDropdownOpen.value = false;
    } else if (isOperationDropdownOpen.value) {
      isOperationDropdownOpen.value = false;
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside, true);
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside, true);
  document.removeEventListener('keydown', handleKeyDown);
  
  if (validationTimeout) {
    clearTimeout(validationTimeout);
  }
});

watch(() => props.data, (newData) => {
  if (newData && newData.selectorsList) {
    originalData.value = JSON.parse(JSON.stringify(newData));
    
    selectorsList.value = JSON.parse(JSON.stringify(newData.selectorsList));
    activeSelectorIndex.value = newData.activeSelectorIndex || 0;

    if (newData.selectorGroupSettings) {
      selectorGroupSettings.value = { ...newData.selectorGroupSettings };
    }
    
    selectorsList.value.forEach((selector, index) => {
      if (selector.isFavorite === undefined) {
        selector.isFavorite = index === 0;
      }
      if (selector.sourceType === undefined) {
        selector.sourceType = 'dataset';
      }
      if (selector.datasetUrl === undefined) {
        selector.datasetUrl = '';
      }
      if (selector.selectedDatasetId === undefined) {
        selector.selectedDatasetId = null;
      }
      if (selector.selectedField === undefined) {
        selector.selectedField = '';
      }
    });
    
    const hasFavorite = selectorsList.value.some(selector => selector.isFavorite);
    if (!hasFavorite && selectorsList.value.length > 0) {
      selectorsList.value[0].isFavorite = true;
    }
    
    if (currentSelector.value.selectedDatasetId) {
      loadAvailableFields();
    }
  }
}, { immediate: true });

watch(() => currentSelector.value, (newSelector) => {
  if (newSelector) {
    urlValidationResult.value = null;
    isUrlValidating.value = false;
    
    if (newSelector.sourceType === 'dataset') {
      sourceInputValue.value = newSelector.selectedDataset || '';
    } else if (newSelector.sourceType === 'url') {
      sourceInputValue.value = newSelector.datasetUrl || '';
      if (newSelector.datasetUrl && newSelector.datasetUrl.trim()) {
        validateUrl(newSelector.datasetUrl.trim());
      }
    }
    
    if (newSelector.selectedDatasetId) {
      loadAvailableFields();
    }
  }
}, { immediate: true });

watch(sourceInputValue, (newValue) => {
  if (!currentSelector.value) return;
  
  if (currentSelector.value.sourceType === 'dataset') {
    return;
  } else if (currentSelector.value.sourceType === 'url') {
    currentSelector.value.datasetUrl = newValue;
  }
});

watch(selectedFieldType, (newFieldType) => {
  if (!newFieldType || !currentSelector.value) return;
  
  const currentSelectorType = currentSelector.value.selectorType;
  const isCurrentTypeAvailable = availableSelectorTypes.value.some(type => type.value === currentSelectorType);
  
  if (!isCurrentTypeAvailable) {
    currentSelector.value.selectorType = 'list';
    currentSelector.value.multipleSelection = false;
  }
  
  const currentOperation = currentSelector.value.operation;
  if (currentOperation) {
    const isCurrentOperationAvailable = availableOperations.value.some(
      op => op.value === currentOperation
    );
    
    if (!isCurrentOperationAvailable) {
      currentSelector.value.operation = '';
    }
  }
});

function onCancel() {
  if (originalData.value) {
    const restoredData = { ...originalData.value };
    if (originalData.value.selectorGroupSettings) {
      restoredData.selectorGroupSettings = { ...originalData.value.selectorGroupSettings };
    }
    emit('save', restoredData);
  }
  emit('close');
}

function updateHintText(value) {
  currentSelector.value.hintText = value;
}

function onSubmit() {
  const settings = {
    ...props.data,
    selectorsList: selectorsList.value,
    activeSelectorIndex: activeSelectorIndex.value,
    selectorGroupSettings: selectorGroupSettings.value
  };
  
  emit('save', settings);
  emit('close');
}
</script>

<style scoped lang="scss">
.widget-settings {
  display: flex;
  border-radius: 8px;
  height: 100%;
  background: var(--color-primary-background);
  overflow: visible;
}

.widget-settings-left-side {
  max-width: 255px;
  min-width: 255px;
  min-height: 300px;
  height: 100%;
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
  background-color: var(--color-background);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: visible;
}

.widget-settings-left-side-title{
  padding: 24px 24px 0 24px;
}

.selectors-list {
  display: flex;
  padding-top: 12px;
  padding-bottom: 12px;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-height: 0;
  overflow: visible;
}

.selectors-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: visible;
  min-height: 0;
}

.selector-list-move {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.selector-list-enter-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.selector-list-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: absolute;
  width: calc(100% - 24px);
  margin: 0 12px;
}

.selector-list-enter-from {
  opacity: 0;
  transform: translateX(-20px) scale(0.95);
}

.selector-list-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.95);
}

.selector-item {
  display: flex;
  align-items: center;
  padding: 12px 12px 12px 12px;
  gap: 12px;
  cursor: pointer;
  color: var(--color-text-primary);
  position: relative;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  border-radius: 6px;
  margin: 0 12px;
  
  &.active {
    background: var(--color-primary-background);
    color: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  
  &:hover:not(.active):not(.dragging) {
    background: var(--color-hover-background);
  }
  
  &.dragging {
    opacity: 0.5;
    transform: rotate(3deg) scale(1.02);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    background: var(--color-primary-background);
    color: white;
  }
  
  &.drag-over {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.3);
    background: var(--color-hover-background);
    
    &::before {
      content: '';
      position: absolute;
      top: -4px;
      left: 12px;
      right: 12px;
      height: 2px;
      background: var(--color-primary);
      border-radius: 1px;
      animation: pulse 1s infinite;
    }
  }
  
  &:hover .delete-selector-btn {
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scaleX(1);
  }
  50% {
    opacity: 0.7;
    transform: scaleX(0.95);
  }
}

.selector-icon {
  display: flex;
  align-items: center;
  gap: 4px;
}

.star-favorite {
  fill: var(--color-warning, #ffc107);
  stroke: var(--color-warning, #ffc107);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: scale(1.1);
    filter: brightness(1.1);
  }
}

.star-regular {
  fill: none;
  stroke: var(--color-text-secondary, #888);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    fill: var(--color-warning-light, rgba(255, 193, 7, 0.2));
    stroke: var(--color-warning, #ffc107);
    transform: scale(1.1);
  }
}

.drag-handle {
  cursor: grab;
  transition: all 0.2s ease;
  color: var(--color-secondary-text);
  
  &:hover {
    color: var(--color-primary);
    transform: scale(1.1);
  }
  
  &:active {
    cursor: grabbing;
    transform: scale(0.95);
  }
}

.selector-item.dragging .drag-handle {
  cursor: grabbing;
  color: white;
}

.selector-name {
  font-size: 14px;
  display: flex;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
  transition: all 0.2s ease;
}

.delete-selector-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 12px;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
  padding: 4px;
  margin-left: auto;
  border-radius: 3px;
  
  &:hover {
    color: #ff4757;
    background: rgba(255, 71, 87, 0.1);
    transform: scale(1.1);
  }
}

.add-selector-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: 2px dashed var(--color-border);
  border-radius: 6px;
  background: none;
  color: var(--color-text-secondary);
  font-size: 14px;
  cursor: pointer;
  margin: 8px 12px 0 12px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  &:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
    background: rgba(var(--color-primary-rgb), 0.05);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.15);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.plus-icon {
  font-size: 12px;
  transition: transform 0.2s ease;
}

.add-selector-btn:hover .plus-icon {
  transform: rotate(90deg);
}

.advanced-settings-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: none;
  background: none;
  color: var(--color-text-secondary);
  font-size: 14px;
  cursor: pointer;
  margin: 0 12px 24px 12px;
  transition: all 0.2s ease;
  border-radius: 0.5rem;
  font-weight: 400;
  
  &:hover {
    color: var(--color-primary);
    background-color: var(--color-hover-background);
    
    .settings-icon {
      transform: rotate(180deg);
    }
  }
}

.settings-icon {
  transition: transform 0.3s ease;
}

.widget-settings-right-side {
  width: 100%;
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: visible;
}

.widget-settings-right-side-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 9px 24px;
  flex-shrink: 0;
}

.widget-settings-right-side-title {
  color: var(--color-text-primary);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--color-secondary-text);
  
  &:hover {
    color: var(--color-primary-text);
  }
}

.close-icon {
  font-size: 32px;
  font-weight: 300;
}

.widget-settings-right-side-content{
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex: 1;
  padding: 3px 24px 0 24px;
  min-height: 0;
}

.settings-table {
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow: visible;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: visible;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.settings-row {
  display: flex;
  align-items: flex-start;
  min-height: 40px;
  overflow: visible;
}

.settings-label {
  width: 215px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  padding-right: 16px;
  
  input[type="checkbox"] {
    margin: 0;
    accent-color: var(--color-accent);
  }
  
  .help-icon {
    color: var(--color-text-secondary);
    cursor: help;
  }
}

.settings-control {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-select {
  background: var(--color-background);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  width: 100%;
  height: 31px;
  transition: border-color 0.2s ease;
  
  &:hover {
    border-color: var(--color-primary-text);
  }
  
  &:focus {
    outline: none;
    border-color: var(--color-primary-text);
    box-shadow: 0 0 0 2px rgba(var(--color-accent-rgb), 0.2);
  }
}

.form-control {
  background: var(--color-background);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
  width: 100%;
  height: 31px;
  transition: border-color 0.2s ease;
  
  &::placeholder {
    color: var(--color-text-secondary);
  }

  &:hover {
    border-color: var(--color-primary-text);
  }
  
  &:focus {
    outline: none;
    border-color: var(--color-primary-text);
    box-shadow: 0 0 0 2px rgba(var(--color-accent-rgb), 0.2);
  }
  
  &.has-icon {
    padding-left: 40px;
  }
  
  &.is-invalid {
    border-color: #ef4444 !important;
    box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2) !important;
    
    &:hover {
      border-color: #ef4444 !important;
      box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2) !important;
    }
    
    &:focus {
      border-color: #ef4444 !important;
      box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.3) !important;
    }
  }
}

.input-group {
  display: flex;
  position: relative;
  overflow: visible;
  align-items: center;
  width: 100%;
  max-width: 100%;
}

.input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  min-width: 0;
}

.input-icon-wrapper {
  position: absolute;
  left: 16px;
  top: 15%;
  transform: translateY(-50%);
  z-index: 2;
  pointer-events: none;
  width: 0;
  height: 0;
  overflow: visible;
}

.input-icon {
  width: 16px;
  height: 16px;
  color: var(--color-accent);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
  text-align: center;
  text-decoration: none;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  border: 1px solid transparent;
  border-radius: 4px;
  transition: all 0.15s ease-in-out;
}

.btn-outline-secondary {
  color: var(--color-text-primary);
  height: 31px;
  background-color: var(--color-background);
  border-color: var(--color-border);
  border-left: none;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  flex-shrink: 0;
  min-width: 80px;
  
  &:hover {
    color: var(--color-text-primary);
    background-color: var(--color-hover-background);
    border-color: var(--color-primary);
  }
  
  &.source-url-error {
    border-color: var(--color-accent) !important;
    box-shadow: 2px 0 0 0 rgba(var(--color-accent-rgb), 0.2), 0 -2px 0 0 rgba(var(--color-accent-rgb), 0.2), 0 2px 0 0 rgba(var(--color-accent-rgb), 0.2) !important;
    
    &:hover {
      border-color: var(--color-accent) !important;
      box-shadow: 2px 0 0 0 rgba(var(--color-accent-rgb), 0.2), 0 -2px 0 0 rgba(var(--color-accent-rgb), 0.2), 0 2px 0 0 rgba(var(--color-accent-rgb), 0.2) !important;
    }
    
    &:focus {
      border-color: var(--color-accent) !important;
      box-shadow: 2px 0 0 0 rgba(var(--color-accent-rgb), 0.3), 0 -2px 0 0 rgba(var(--color-accent-rgb), 0.3), 0 2px 0 0 rgba(var(--color-accent-rgb), 0.3) !important;
    }
  }
  
  &.source-url-success {
    border-color: var(--color-success, #22c55e) !important;
    box-shadow: 2px 0 0 0 rgba(34, 197, 94, 0.2), 0 -2px 0 0 rgba(34, 197, 94, 0.2), 0 2px 0 0 rgba(34, 197, 94, 0.2) !important;
    
    &:hover {
      border-color: var(--color-success, #22c55e) !important;
      box-shadow: 2px 0 0 0 rgba(34, 197, 94, 0.2), 0 -2px 0 0 rgba(34, 197, 94, 0.2), 0 2px 0 0 rgba(34, 197, 94, 0.2) !important;
    }
    
    &:focus {
      border-color: var(--color-success, #22c55e) !important;
      box-shadow: 2px 0 0 0 rgba(34, 197, 94, 0.3), 0 -2px 0 0 rgba(34, 197, 94, 0.3), 0 2px 0 0 rgba(34, 197, 94, 0.3) !important;
    }
  }
}

.dropdown-toggle {
  position: relative;
  
  &::after {
    content: '';
    display: inline-block;
    margin-left: 6px;
    vertical-align: middle;
    border-top: 4px solid;
    border-right: 4px solid transparent;
    border-bottom: 0;
    border-left: 4px solid transparent;
  }
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 9999;
  display: block;
  min-width: 120px;
  margin: 2px 0 0 0;
  padding: 0.5rem 0;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  list-style: none;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 8px 12px;
  clear: both;
  font-weight: 400;
  color: var(--color-text-primary);
  text-align: inherit;
  text-decoration: none;
  white-space: nowrap;
  background-color: transparent;
  border: 0;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: var(--color-hover-background);
    color: var(--color-text-primary);
  }
  
  &.active {
    background-color: var(--bs-primary-border-subtle);
    color: white;
    
    &:hover {
      background-color: var(--bs-primary);
      color: white;
    }
  }
}

.link-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 12px;
  cursor: pointer;
  padding: 4px 0;
  text-decoration: underline;
  
  &:hover {
    color: var(--color-primary-dark);
  }
}

.title-position-buttons {
  display: flex;
  width: 100%;
}

.position-btn {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text-primary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  
  &:hover {
    border-color: var(--color-primary);
    background: var(--color-hover-background);
    border-width: 1px !important;
  }
  
  &.active {
    background: var(--color-primary-background);
    color: var(--color-primary-text);
    font-weight: 650;
    border-color: var(--color-primary);
    border-width: 1px !important;
  }
}

.widget-settings-right-side-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 24px 24px 24px;
  background: var(--color-primary-background);
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.validation-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  border-radius: 4px;
  color: #ef4444;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  
  &.clickable {
    cursor: pointer;
    
    &:hover {
      background-color: rgba(239, 68, 68, 0.15);
      border-color: #dc2626;
      transform: translateY(-1px);
    }
  }
}

.validation-hint .hint-icon {
  flex-shrink: 0;
  width: 14px;
  height: 14px;
}

.validation-hint .hint-text {
  flex: 1;
}

.validation-hint .hint-action {
  font-size: 11px;
  opacity: 0.8;
  font-style: italic;
  margin-left: 8px;
}

button.cancel {
  background: none;
  color: var(--color-secondary-text);
  border: none;
  font-size: 16px;
  cursor: pointer;
}

button.cancel:hover {
  color: var(--color-primary-text);
  transition: background 0.2s, color 0.2s, opacity 0.2s;
  cursor: pointer;
}

.btn.btn-primary {
  border: none;
  border-radius: 6px;
  padding: 8px 24px;
  font-size: 16px;
  cursor: pointer;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: var(--color-border);
    color: var(--color-text-secondary);
  }
}

.dataset-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.dataset-modal-container {
  background: var(--color-primary-background);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  max-width: 450px;
  width: 90vw;
  max-height: 600px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dataset-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px 24px;
  flex-shrink: 0;
}

.dataset-modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-primary-text);
  margin: 0;
}

.dataset-modal-close {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--color-secondary-text);
  border-radius: 6px;
  
  &:hover {
    color: var(--color-primary-text);
    background: var(--color-hover-background);
  }
  
  .close-icon {
    font-size: 24px;
    font-weight: 300;
  }
}

.dataset-modal-content {
  padding: 0px 24px 24px 24px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.url-validation-result {
  background-color: transparent;
  border: none;
  display: flex;
  align-items: center;
  gap: 0;
  font-size: 13px;
}

.validation-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6366f1;
  font-weight: 500;
  width: 100%;
}

.loading-spinner {
  border: 2px solid rgba(99, 102, 241, 0.3);
  border-top: 2px solid #6366f1;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
  flex-shrink: 0;
}

.loading-text {
  color: #6366f1;
  font-weight: 500;
}

.validation-message {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  width: 100%;
}

.validation-icon {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
}

.validation-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.dataset-info {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 2px;
}

.dataset-info strong {
  font-weight: 600;
}

.success-message {
  color: #22c55e;
  display: flex;
  align-items: center;
}

.success-message .validation-icon {
  color: #22c55e;
  display: flex;
}

.error-message {
  color: #ef4444;
  display: flex;
  align-items: center;
}

.error-message .validation-icon {
  color: #ef4444;
  display: flex;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.source-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.form-control {
  background: var(--color-background);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
  width: 100%;
  height: 31px;
  transition: border-color 0.2s ease;
  
  &::placeholder {
    color: var(--color-text-secondary);
  }
  
  &:focus {
    outline: none;
    border-color: var(--color-primary-text);
    box-shadow: 0 0 0 2px rgba(var(--color-accent-rgb), 0.2);
  }
  
  &.source-select-mode {
    cursor: pointer;
    user-select: none;
    caret-color: transparent;
    
    &:focus {
      outline: none;
      border-color: var(--color-primary-text);
      box-shadow: 0 0 0 2px rgba(var(--color-accent-rgb), 0.2);
    }
  }
  
  &.has-icon {
    padding-left: 40px;
  }
  
  &.source-url-error {
    border-color: var(--color-accent) !important;
    box-shadow: -2px 0 0 0 rgba(var(--color-accent-rgb), 0.2), 0 -2px 0 0 rgba(var(--color-accent-rgb), 0.2), 0 2px 0 0 rgba(var(--color-accent-rgb), 0.2) !important;
    
    &:focus {
      border-color: var(--color-accent) !important;
      box-shadow: -2px 0 0 0 rgba(var(--color-accent-rgb), 0.3), 0 -2px 0 0 rgba(var(--color-accent-rgb), 0.3), 0 2px 0 0 rgba(var(--color-accent-rgb), 0.3) !important;
    }
  }
  
  &.source-url-success {
    border-color: var(--color-success, #22c55e) !important;
    box-shadow: -2px 0 0 0 rgba(34, 197, 94, 0.2), 0 -2px 0 0 rgba(34, 197, 94, 0.2), 0 2px 0 0 rgba(34, 197, 94, 0.2) !important;
    
    &:focus {
      border-color: var(--color-success, #22c55e) !important;
      box-shadow: -2px 0 0 0 rgba(34, 197, 94, 0.3), 0 -2px 0 0 rgba(34, 197, 94, 0.3), 0 2px 0 0 rgba(34, 197, 94, 0.3) !important;
    }
  }
}

.form-control-button{
  &:hover {
    border-color: var(--color-primary-text);
    background-color: var(--color-hover-background);
  }
}

.input-group {
  display: flex;
  position: relative;
  overflow: visible;
  align-items: center;
  width: 100%;
  max-width: 100%;
}

.input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  min-width: 0;
}

.input-icon-wrapper {
  position: absolute;
  left: 16px;
  top: 3%;
  transform: translateY(-50%);
  z-index: 2;
  pointer-events: none;
  width: 0;
  height: 0;
  overflow: visible;
}

.input-icon {
  width: 16px;
  height: 16px;
  color: var(--color-accent);
}

.btn-outline-secondary {
  color: var(--color-text-primary);
  background-color: var(--color-background);
  border-color: var(--color-border);
  border-left: none;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  flex-shrink: 0;
  min-width: 80px;
  
  &:hover {
    color: var(--color-text-primary);
    background-color: var(--color-hover-background);
    border-color: var(--color-primary);
  }
  
  &.source-url-error {
    border-color: var(--color-accent) !important;
    box-shadow: 2px 0 0 0 rgba(var(--color-accent-rgb), 0.2), 0 -2px 0 0 rgba(var(--color-accent-rgb), 0.2), 0 2px 0 0 rgba(var(--color-accent-rgb), 0.2) !important;
    
    &:hover {
      border-color: var(--color-accent) !important;
      box-shadow: 2px 0 0 0 rgba(var(--color-accent-rgb), 0.2), 0 -2px 0 0 rgba(var(--color-accent-rgb), 0.2), 0 2px 0 0 rgba(var(--color-accent-rgb), 0.2) !important;
    }
    
    &:focus {
      border-color: var(--color-accent) !important;
      box-shadow: 2px 0 0 0 rgba(var(--color-accent-rgb), 0.3), 0 -2px 0 0 rgba(var(--color-accent-rgb), 0.3), 0 2px 0 0 rgba(var(--color-accent-rgb), 0.3) !important;
    }
  }
  
  &.source-url-success {
    border-color: var(--color-success, #22c55e) !important;
    box-shadow: 2px 0 0 0 rgba(34, 197, 94, 0.2), 0 -2px 0 0 rgba(34, 197, 94, 0.2), 0 2px 0 0 rgba(34, 197, 94, 0.2) !important;
    
    &:hover {
      border-color: var(--color-success, #22c55e) !important;
      box-shadow: 2px 0 0 0 rgba(34, 197, 94, 0.2), 0 -2px 0 0 rgba(34, 197, 94, 0.2), 0 2px 0 0 rgba(34, 197, 94, 0.2) !important;
    }
    
    &:focus {
      border-color: var(--color-success, #22c55e) !important;
      box-shadow: 2px 0 0 0 rgba(34, 197, 94, 0.3), 0 -2px 0 0 rgba(34, 197, 94, 0.3), 0 2px 0 0 rgba(34, 197, 94, 0.3) !important;
    }
  }
}

.dropdown-toggle {
  position: relative;
  
  &::after {
    content: '';
    display: inline-block;
    margin-left: 6px;
    vertical-align: middle;
    border-top: 4px solid;
    border-right: 4px solid transparent;
    border-bottom: 0;
    border-left: 4px solid transparent;
  }
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 9999;
  display: block;
  min-width: 120px;
  margin: 2px 0 0 0;
  padding: 0.5rem 0;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  list-style: none;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 8px 12px;
  clear: both;
  font-weight: 400;
  color: var(--color-text-primary);
  text-align: inherit;
  text-decoration: none;
  white-space: nowrap;
  background-color: transparent;
  border: 0;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: var(--color-hover-background);
    color: var(--color-text-primary);
  }
  
  &.active {
    background-color: var(--bs-primary-border-subtle);
    color: white;
    
    &:hover {
      background-color: var(--bs-primary);
      color: white;
    }
  }
}

.operation-dropdown {
  position: relative;
  width: 100%;
}

.operation-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  height: 31px;
  padding: 8px 12px;
  background: var(--color-background);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--color-primary-text);
  }
  
  &.open {
    border-color: var(--color-primary-text);
    box-shadow: 0 0 0 2px rgba(var(--color-accent-rgb), 0.2);
  }
}

.operation-text {
  flex: 1;
  text-align: left;
  font-size: 14px;
}

.operation-toggle.open .dropdown-arrow {
  transform: rotate(180deg);
}

.operation-menu {
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
  margin-top: 2px;
}

.operation-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: var(--color-hover-background);
  }
  
  &.active {
    background: var(--color-primary-background);
    color: white;
  }
}

.selector-type-dropdown {
  position: relative;
  width: 100%;
}

.selector-type-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  height: 31px;
  padding: 8px 12px;
  background: var(--color-background);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--color-primary-text);
  }
  
  &.open {
    border-color: var(--color-primary-text);
    box-shadow: 0 0 0 2px rgba(var(--color-accent-rgb), 0.2);
  }
}

.selector-type-icon {
  display: flex;
  align-items: center;
  color: var(--color-accent);
}

.selector-type-text {
  flex: 1;
  text-align: left;
}

.dropdown-arrow {
  color: var(--color-text-secondary);
  transition: transform 0.2s ease;
}

.selector-type-toggle.open .dropdown-arrow {
  transform: rotate(180deg);
}

.selector-type-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  margin-top: 2px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.selector-type-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: var(--color-hover-background);
  }
  
  &.active {
    background: var(--color-primary-background);
    color: white;
    
    .selector-type-icon {
      color: white;
    }
  }
  
  .selector-type-icon {
    color: var(--color-accent);
    transition: color 0.2s ease;
  }
  
  &:hover .selector-type-icon {
    color: var(--color-accent);
  }
  
  &.active .selector-type-icon {
    color: white;
  }
  
  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
    color: var(--color-text-secondary);
    
    &:hover {
      background: transparent;
    }
    
    .selector-type-icon {
      color: var(--color-text-secondary);
    }
    
    &:hover .selector-type-icon {
      color: var(--color-text-secondary);
    }
  }
}

.disabled-indicator {
  margin-left: auto;
  color: var(--color-text-secondary);
  opacity: 0.7;
}



.help-icon-wrapper {
  position: relative;
  display: inline-block;
}

.custom-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-background);
  color: var(--color-text-primary);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 400;
  white-space: normal;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--color-border);
  margin-bottom: 8px;
  max-width: 250px;
  min-width: 150px;
  width: max-content;
  word-wrap: break-word;
  text-align: center;
  
  &::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid var(--color-background);
    filter: drop-shadow(0 1px 0 var(--color-border));
  }
}

.settings-label {
  position: relative;
}

.text-editor-wrapper {
  max-width: 100%;
  overflow: hidden;
  
  :deep(.text-editor) {
    max-width: 100%;
    width: 100%;
    
    .editor-toolbar {
      flex-wrap: wrap;
      gap: 2px;
      
      .toolbar-formatting,
      .toolbar-styles,
      .toolbar-actions {
        flex-wrap: wrap;
      }
    }
    
    .editor-content {
      max-width: 100%;
      
      .editor-textarea {
        max-width: 100%;
        word-wrap: break-word;
        overflow-wrap: break-word;
      }
    }
  }
}

.field-selector-container {
  position: relative;
  width: 100%;
}

.custom-field-select {
  position: relative;
  width: 100%;
}

.field-select-button {
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

.field-select-text {
  flex: 1;
  text-align: left;
}

.selected-field-icon {
  margin-right: 8px;
  margin-left: 0;
}

.dropdown-arrow {
  color: var(--color-text-secondary);
  transition: transform 0.2s ease;
  
  .open & {
    transform: rotate(180deg);
  }
}

.field-dropdown-menu {
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
  margin-top: 2px;
}

.field-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: var(--color-hover-background);
  }
  
  &.selected {
    background: var(--color-primary-background);
    color: white;
    
    .field-icon {
      color: white;
    }
  }
}

.field-name {
  flex: 1;
  text-align: left;
  font-size: 14px;
}

.field-icon {
  flex-shrink: 0;
}

.no-field-selected {
  display: flex;
  align-items: center;
  height: 31px;
  padding: 4px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background-muted);
  
  .text-muted {
    color: var(--color-text-secondary);
    font-size: 14px;
  }
}

.default-value-selector-container {
  width: 100%;
  
  &.is-invalid {
    :deep(.default-value-selector) {
      border-color: #ef4444 !important;
      box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2) !important;
      
      &:hover {
        border-color: #ef4444 !important;
        box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2) !important;
      }
      
      &:focus-within {
        border-color: #ef4444 !important;
        box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.3) !important;
      }
    }
  }
}

.default-input-container {
  width: 100%;
}

.default-input-container .form-control.input-sm {
  height: 31px;
  font-size: 14px;
  padding: 4px 12px;
}

.invalid-feedback {
  display: block;
  color: #ef4444;
  font-size: 12px;
  font-weight: 500;
  margin-top: 4px;
  padding-left: 4px;
}

.other-selector-type {
  display: flex;
  align-items: center;
  height: 31px;
  padding: 4px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background-muted);
  
  .text-muted {
    color: var(--color-text-secondary);
    font-size: 14px;
  }
}

/* Стили для модального окна расширенных настроек */
.advanced-settings-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.advanced-settings-modal-container {
  background: var(--color-primary-background);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.advanced-settings-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px 24px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--color-border);
}

.advanced-settings-modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-primary-text);
  margin: 0;
}

.advanced-settings-modal-close {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--color-secondary-text);
  border-radius: 6px;
  
  &:hover {
    color: var(--color-primary-text);
    background: var(--color-hover-background);
  }
  
  .close-icon {
    font-size: 24px;
    font-weight: 300;
  }
}

.advanced-settings-modal-content {
  padding: 24px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-primary-text);
  cursor: pointer;
}

.setting-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--color-accent);
  cursor: pointer;
}

.setting-hint {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-left: 26px;
  line-height: 1.4;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.modal-actions .btn {
  padding: 8px 20px;
  border-radius: 0.5rem;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}
</style>