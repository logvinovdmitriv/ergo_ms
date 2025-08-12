<script setup>
const props = defineProps({
  makeCenter: { type: Boolean, default: false },
  dropdownMenuClass: { type: String, default: '' },
  offset: { type: String, default: '0,0' },
  inset: { type: String, default: '0 0 auto auto' },
  transform: { type: String, default: 'translate(0px, 40px)' },
})
</script>

<template>
  <div :class="makeCenter ? 'dropdown-center' : 'dropdown'">
    <div
      class="dropdown-button rounded p-2"
      data-bs-toggle="dropdown"
      aria-expanded="false"
      :data-bs-offset="offset"
    >
      <slot name="main"></slot>
    </div>
    <ul
      class="dropdown-menu"
      :class="dropdownMenuClass"
      :style="{
        inset: props.inset,
        transform: props.transform,
      }"
    >
      <slot name="list"></slot>
    </ul>
  </div>
</template>

<style lang="scss">
// Кнопка открытия
.dropdown-button {
  cursor: pointer;
  transition: all $transition;

  &:hover {
    background-color: var(--color-secondary-background);
  }
}

// Пункт меню
.dropdown-item {
  @include flex-row-gap(0.625rem, center);
  transition: all $transition;
  padding: $padding-internal $padding-external;
  cursor: pointer;
}

// Анимация
.dropdown .dropdown-menu,
.dropdown-center .dropdown-menu {
  background-color: var(--bs-card-bg);

  transition:
    max-height 0.3s,
    opacity 0.2s 0.1s,
    visibility 0s 0.3s;

  max-height: 0;
  display: block;
  overflow: hidden;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}
.dropdown .dropdown-menu-end {
  inset: 0 0 auto auto;
  transform: translate(0px, 40px);
}

.dropdown .dropdown-menu.show,
.dropdown-center .dropdown-menu.show {
  transition:
    max-height 0.3s,
    opacity 0.2s,
    visibility 0s;

  max-height: 190px;
  opacity: 1;
  visibility: visible;
  pointer-events: all;
}

.dropdown .dropdown-menu .dropdown-item,
.dropdown-center .dropdown-menu .dropdown-item {
  opacity: 0;
  transform: translateY(-10px);

  transition:
    opacity 0.5s ease,
    transform 0.5s ease;
}

.dropdown .dropdown-menu.show .dropdown-item,
.dropdown-center .dropdown-menu.show .dropdown-item {
  opacity: 1;
  transform: translateY(0);
}
</style>
