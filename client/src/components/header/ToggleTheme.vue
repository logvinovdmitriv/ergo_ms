<script setup>
import { LaptopMinimal, Moon, Sun } from 'lucide-vue-next'
import { computed, ref } from 'vue'

const theme = ref(localStorage.getItem('theme') || 'auto')

// Изменение темы
const changeTheme = (newTheme) => {
  theme.value = newTheme
  localStorage.setItem('theme', newTheme)

  if (newTheme === 'auto') {
    const clientTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    document.documentElement.setAttribute('data-bs-theme', clientTheme)
  } else {
    document.documentElement.setAttribute('data-bs-theme', newTheme)
  }
}

// Установка иконки
const currentIcon = computed(() => {
  if (theme.value === 'light') return Sun
  if (theme.value === 'dark') return Moon
  return LaptopMinimal
})

// Список тем
const themes = ref([
  { icon: Sun, title: 'Светлая', theme: 'light' },
  { icon: Moon, title: 'Тёмная', theme: 'dark' },
  { icon: LaptopMinimal, title: 'Системная', theme: 'auto' },
])
</script>

<template>
  <div class="dropdown-center header-dropdown-center">
    <div data-bs-toggle="dropdown" aria-expanded="false" data-bs-offset="0,20">
      <div class="header-btn" v-tooltip title="Внешний вид">
        <component :is="currentIcon" :size="24" />
      </div>
    </div>
    <ul class="dropdown-menu header-dropdown-menu">
      <li
        v-for="(item, index) in themes"
        :key="index"
        @click="changeTheme(item.theme)"
        class="dropdown-item header-dropdown-item"
        :class="{ active: theme === item.theme }"
        :style="{ transitionDelay: `${index * 50}ms` }"
      >
        <span class="icon-flex">
          <component :is="item.icon" :size="22" />
        </span>
        <span>{{ item.title }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped lang="scss"></style>
