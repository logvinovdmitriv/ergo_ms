<template>
  <form @submit.prevent="submit">
    <div class="grid">
      <label>
        <span>Название</span>
        <input v-model="form.name" required />
      </label>
      <label>
        <span>Slug</span>
        <input v-model="form.slug" />
      </label>
      <label class="col-span-2">
        <span>Описание</span>
        <textarea v-model="form.description" rows="3" />
      </label>
      <label>
        <span>Видимость</span>
        <select v-model="form.visibility">
          <option value="private">Private</option>
          <option value="internal">Internal</option>
          <option value="public">Public</option>
        </select>
      </label>
      <label>
        <span>Макс. проектов</span>
        <input type="number" min="0" v-model.number="form.max_projects" />
      </label>
      <label>
        <span>Billing name</span>
        <input v-model="form.billing_name" />
      </label>
      <label>
        <span>Billing email</span>
        <input type="email" v-model="form.billing_email" />
      </label>
    </div>
    <div class="actions">
      <button type="button" class="btn" @click="$emit('cancel')">Отмена</button>
      <button type="submit" class="btn btn-primary">Сохранить</button>
    </div>
  </form>

</template>

<script>
export default {
  name: 'OrganizationEditFields',
  props: { initial: { type: Object, required: true } },
  data() {
    return {
      form: {
        name: this.initial?.name || '',
        slug: this.initial?.slug || '',
        description: this.initial?.description || '',
        visibility: this.initial?.visibility || 'private',
        max_projects: this.initial?.max_projects ?? null,
        billing_name: this.initial?.billing_name || '',
        billing_email: this.initial?.billing_email || '',
      }
    };
  },
  watch: {
    initial: {
      deep: true,
      handler(v) {
        this.form = { ...this.form, ...v };
      }
    }
  },
  methods: {
    submit() {
      const patch = { ...this.form };
      Object.keys(patch).forEach(k => patch[k] === '' && (patch[k] = null));
      this.$emit('save', patch);
    }
  }
};
</script>

<style scoped>
.grid { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: .75rem; }
.col-span-2 { grid-column: span 2 / span 2; }
label span { display:block; font-size:.85rem; color:#6b7280; margin-bottom:.25rem; }
input, textarea, select { width:100%; border:1px solid #e5e7eb; border-radius:6px; padding:.5rem .6rem; }
.actions { display:flex; justify-content:flex-end; gap:.5rem; margin-top:.75rem; }
.btn { padding:.5rem .75rem; border-radius:6px; background:#f3f4f6; }
.btn-primary { background:#2563eb; color:white; }
</style>
