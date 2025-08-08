import { 
  Type, 
  Hash, 
  Calendar, 
  Clock, 
  MapPin, 
  Map, 
  ToggleLeft, 
  Percent 
} from 'lucide-vue-next';

// Маппинг типов данных на иконки
export const fieldTypeIcons = {
  'string': Type,
  'integer': Hash,
  'float': Percent,
  'date': Calendar,
  'date&time': Clock,
  'geopoint': MapPin,
  'geopolygon': Map,
  'bool': ToggleLeft
};

// Функция для получения иконки по типу данных
export function getFieldTypeIcon(fieldType) {
  return fieldTypeIcons[fieldType] || Type; // По умолчанию Type для неизвестных типов
}

// Функция для получения цвета иконки по типу данных
export function getFieldTypeColor(fieldType) {
  const colors = {
    'string': '#3B82F6',      // blue
    'integer': '#10B981',     // green
    'float': '#F59E0B',       // amber
    'date': '#8B5CF6',        // violet
    'date&time': '#EC4899',   // pink
    'geopoint': '#EF4444',    // red
    'geopolygon': '#06B6D4',  // cyan
    'bool': '#6B7280'         // gray
  };
  
  return colors[fieldType] || '#6B7280';
}

// Функция для получения подсказки по типу данных
export function getFieldTypeTooltip(fieldType) {
  const tooltips = {
    'string': 'Строка',
    'integer': 'Целое число',
    'float': 'Дробное число',
    'date': 'Дата',
    'date&time': 'Дата и время',
    'geopoint': 'Геоточка',
    'geopolygon': 'Геополигон',
    'bool': 'Логический'
  };
  
  return tooltips[fieldType] || 'Неизвестный тип';
} 