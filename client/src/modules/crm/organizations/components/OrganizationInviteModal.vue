<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal card">
      <header class="card__header">
        <h3 class="card__title">Пригласить в «{{ org?.name || 'организацию' }}»</h3>
      </header>
      <div class="card__body">
        <form @submit.prevent="submit">
          <div class="form-row">
            <label>Email<span class="req">*</span></label>
            <input v-model.trim="email" type="email" required class="input" placeholder="user@example.com" />
          </div>

          <div class="form-row">
            <label>Роль</label>
            <select v-model="role" class="select">
              <option value="member">member</option>
              <option value="viewer">viewer</option>
              <option value="admin">admin</option>
            </select>
          </div>

          <footer class="form-actions">
            <button class="btn btn--ghost" type="button" @click="$emit('close')">Отмена</button>
            <button class="btn btn--primary" :disabled="loading" type="submit">Отправить</button>
          </footer>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrganizationInviteModal',
  props: {
    org: { type: Object, default: () => ({}) },
    loading: { type: Boolean, default: false }
  },
  data() {
    return { email: '', role: 'member' }
  },
  methods: {
    submit() {
      if (!this.email) return;
      this.$emit('submit', { email: this.email, role: this.role });
    }
  }
}
</script>

<style scoped lang="scss">
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.35);
  display:flex; align-items:center; justify-content:center; z-index: 50;
}
.modal { width: 100%; max-width: 520px; }
.form-actions { display:flex; gap:8px; justify-content:flex-end; margin-top: 8px; }
</style>
