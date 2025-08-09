<template>
  <div class="orgs-modal">
    <div class="orgs-modal__backdrop" @click="$emit('close')" />

    <div class="orgs-modal__dialog" role="dialog" aria-modal="true">
      <header class="orgs-modal__header">
        <h3 class="orgs-modal__title">Пригласить участника</h3>
        <button class="orgs-modal__close btn btn--ghost" @click="$emit('close')" aria-label="Закрыть">✕</button>
      </header>

      <form class="orgs-modal__body" @submit.prevent="$emit('submit', { email, role })">
        <div class="form-row">
          <label>Email</label>
          <input v-model.trim="email" class="input" type="email" required placeholder="user@example.com" />
        </div>

        <div class="form-row">
          <label>Роль</label>
          <select v-model="role" class="select" required>
            <option value="member">member</option>
            <option value="viewer">viewer</option>
            <option value="admin">admin</option>
          </select>
        </div>

        <footer class="orgs-modal__actions">
          <button type="button" class="btn btn--ghost" @click="$emit('close')">Отмена</button>
          <button type="submit" class="btn btn--primary" :disabled="loading">Отправить</button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, watchEffect } from 'vue';
export default {
  name: 'OrganizationInviteModal',
  props: { org: Object, loading: Boolean },
  setup() {
    const email = ref('');
    const role = ref('member');

    watchEffect(() => {
      // сброс при открытии/закрытии можно добавить по месту
    });

    return { email, role };
  }
};
</script>
