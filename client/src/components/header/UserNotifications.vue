<script setup>
import { Bell } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const router = useRouter()

const notificationGoTo = (routeName) => {
  router.push({ name: routeName })
}
</script>

<template>
  <div class="dropdown-center header-dropdown-center">
    <div data-bs-toggle="dropdown" aria-expanded="false" data-bs-offset="0,20">
      <div class="header-btn" v-tooltip title="Уведомления">
        <Bell :size="24" />
      </div>
    </div>
    <ul class="dropdown-menu header-dropdown-menu">
      <li class="dropdown-item d-block" @click="notificationGoTo('Messenger')">
        <p class="fw-bold mb-0">Сообщение!</p>
        <span class="text-primary">Перейти ➝</span>
      </li>
      <li class="dropdown-item d-block" @click="notificationGoTo('Email')">
        <p class="fw-bold mb-0">Письмо!</p>
        <span class="text-primary">Перейти ➝</span>
      </li>
    </ul>
  </div>
</template>

<style scoped lang="scss"></style>
