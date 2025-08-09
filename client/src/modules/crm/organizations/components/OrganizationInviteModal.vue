<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal card">
      <header class="card__header">
        <h3 class="card__title">Пригласить участника</h3>
      </header>
      <form class="card__body" @submit.prevent="submit">
        <div class="form-row">
          <label>Email<span class="req">*</span></label>
          <input v-model.trim="email" type="email" class="input" required placeholder="user@example.com" />
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
          <button class="btn btn--primary" :disabled="loading" type="submit">Отправить</button>
          <button class="btn btn--ghost" type="button" @click="$emit('close')">Отмена</button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrganizationInviteModal',
  props: { org: { type: Object, required: true }, loading: Boolean },
  emits: ['close', 'submit'],
  data: () => ({ email: '', role: 'member' }),
  methods: {
    submit() { this.$emit('submit', { email: this.email, role: this.role }); }
  }
}
</script>

<style scoped>
.modal-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:50}
.modal{width:min(560px, 92vw)}
</style>
