<template>
  <teleport to="body">
    <!-- фон -->
    <div class="org-invite__backdrop" @click="onBackdrop" />

    <!-- окно -->
    <div class="org-invite__wrap" role="dialog" aria-modal="true">
      <div class="org-invite__modal">
        <header class="org-invite__header">
          <h3>Пригласить пользователя</h3>
          <button class="btn btn--xs btn--ghost" @click="$emit('close')" :disabled="loading">×</button>
        </header>

        <div class="org-invite__body">
          <label class="fi">
            <span>Email</span>
            <input v-model.trim="email" class="input" type="email" placeholder="user@example.com" />
          </label>

          <label class="fi">
            <span>Роль</span>
            <select v-model="role" class="input">
              <option value="member">member</option>
              <option value="admin">admin</option>
              <option value="viewer">viewer</option>
            </select>
            <small class="muted">По умолчанию: {{ org?.default_role || 'member' }}</small>
          </label>
        </div>

        <footer class="org-invite__footer">
          <button class="btn btn--ghost" @click="$emit('close')" :disabled="loading">Отмена</button>
          <button class="btn btn--primary" @click="submit" :disabled="loading || !canSubmit">
            {{ loading ? 'Отправляем…' : 'Отправить' }}
          </button>
        </footer>
      </div>
    </div>
  </teleport>
</template>

<script>
export default {
  name: 'OrganizationInviteModal',
  props: {
    org: { type: Object, default: () => ({}) },
    loading: { type: Boolean, default: false },
  },
  emits: ['close', 'submit'],
  data() {
    return {
      email: '',
      role: this.org?.default_role && ['member', 'admin', 'viewer'].includes(this.org.default_role)
        ? this.org.default_role
        : 'member',
    };
  },
  computed: {
    canSubmit() {
      return this.email.length > 3 && this.email.includes('@');
    }
  },
  mounted() {
    // ESC закрывает
    this._esc = (e) => { if (e.key === 'Escape') this.$emit('close'); };
    window.addEventListener('keydown', this._esc);
    // фокус на инпут
    this.$nextTick(() => {
      const el = document.querySelector('.org-invite__modal input[type="email"]');
      el && el.focus();
    });
    // блокируем скролл страницы
    document.documentElement.classList.add('no-scroll');
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this._esc);
    document.documentElement.classList.remove('no-scroll');
  },
  methods: {
    onBackdrop(e) {
      // клик по фону — закрыть
      this.$emit('close');
    },
    submit() {
      if (!this.canSubmit) return;
      this.$emit('submit', { email: this.email, role: this.role });
    },
  },
};
</script>

<style scoped>
/* Высокий z-index, чтобы перекрыть всё */
.org-invite__backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.5);
  z-index: 10000;
}
.org-invite__wrap {
  position: fixed; inset: 0;
  display: grid; place-items: center;
  z-index: 10001;
  padding: 16px;
}
.org-invite__modal {
  width: 100%;
  max-width: 520px;
  background: var(--card-bg, #111418);
  color: inherit;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,.35);
  overflow: hidden;
}
.org-invite__header,
.org-invite__footer {
  display:flex; align-items:center; justify-content:space-between;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.org-invite__footer { border-top: 1px solid rgba(255,255,255,.06); border-bottom:none; gap:8px; }
.org-invite__body { padding: 14px; display: grid; gap: 12px; }
.fi { display: grid; gap: 6px; }
.input { width:100%; padding: 8px 10px; border:1px solid #3b3f46; border-radius: 6px; background: transparent; color: inherit; }
.muted { color: #9aa0a6; font-size: 12px; }
.btn { cursor: pointer; }
.no-scroll { overflow: hidden; }
</style>
