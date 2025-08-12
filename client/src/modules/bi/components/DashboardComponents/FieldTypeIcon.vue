<template>
  <div 
    class="field-type-icon" 
    :title="tooltip"
    :style="{ color: iconColor }"
  >
    <component :is="iconComponent" :size="size" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { getFieldTypeIcon, getFieldTypeColor, getFieldTypeTooltip } from './js/fieldTypeIcons.js';

const props = defineProps({
  fieldType: {
    type: String,
    required: true
  },
  size: {
    type: Number,
    default: 16
  }
});

const iconComponent = computed(() => {
  return getFieldTypeIcon(props.fieldType);
});

const iconColor = computed(() => {
  return getFieldTypeColor(props.fieldType);
});

const tooltip = computed(() => {
  return getFieldTypeTooltip(props.fieldType);
});
</script>

<style scoped>
.field-type-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style> 