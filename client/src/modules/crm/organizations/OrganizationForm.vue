<template>
  <section class="card">
    <header class="card__header">
      <h2 class="card__title">Новая организация</h2>
      <div class="muted">Заполните основные сведения. Имя и сайт — самые важные для начала.</div>
    </header>

    <form class="card__body form-grid" @submit.prevent="save">
      <div class="form-row">
        <label>Название<span class="req">*</span></label>
        <input v-model.trim="form.name" class="input" required placeholder="ООО «Ромашка»" />
      </div>

      <div class="form-row">
        <label>Адрес (slug)</label>
        <input v-model.trim="form.slug" class="input" placeholder="romashka" />
        <small class="muted">Автогенерируется из названия, можно изменить.</small>
      </div>

      <div class="form-row">
        <label>Описание</label>
        <textarea v-model="form.description" class="input" rows="3" />
      </div>

      <div class="form-row">
        <label>Сайт</label>
        <input v-model.trim="form.website" class="input" type="url" placeholder="https://example.com" />
        <small class="muted">Укажите корпоративный сайт (опционально)</small>
      </div>

      <div class="form-row">
        <label>Email</label>
        <input v-model.trim="form.email" class="input" type="email" />
      </div>

      <div class="form-row">
        <label>Телефон</label>
        <input v-model.trim="form.phone" class="input" />
      </div>

      <div class="form-row">
        <label>Страна</label>
        <input v-model.trim="form.country" class="input" />
      </div>

      <div class="form-row">
        <label>Часовой пояс</label>
        <input v-model.trim="form.timezone" class="input" placeholder="Europe/Moscow" />
        <small class="muted">Например: Europe/Moscow</small>
      </div>

      <div class="form-row">
        <label>Адрес</label>
        <input v-model.trim="form.address" class="input" />
      </div>

      <div class="form-row">
        <label>Отрасль</label>
        <input v-model.trim="form.industry" class="input" />
      </div>

      <div class="form-row">
        <label>Видимость</label>
        <select v-model="form.visibility" class="select">
          <option value="by_invite">by_invite</option>
          <option value="private">private</option>
        </select>
      </div>

      <div class="form-row">
        <label>Роль по умолчанию</label>
        <select v-model="form.default_role" class="select">
          <option value="member">member</option>
          <option value="viewer">viewer</option>
        </select>
      </div>

      <div class="form-row">
        <label>Статус</label>
        <select v-model="form.status" class="select">
          <option value="active">active</option>
          <option value="archived">archived</option>
        </select>
      </div>

      <div class="form-row col-2">
        <div>
        <label>Плательщик (Billing name)</label>
          <input v-model.trim="form.billing_name" class="input" />
        </div>
        <div>
          <label>VAT</label>
          <input v-model.trim="form.billing_vat" class="input" />
        </div>
      </div>

      <div class="form-row">
        <label>Платёжный адрес (Billing address)</label>
        <input v-model.trim="form.billing_address" class="input" />
      </div>

      <footer class="form-actions">
        <button class="btn btn--primary" type="submit" :disabled="!canSubmit || saving">Создать</button>
        <router-link class="btn btn--ghost" :to="{ name: 'OrganizationList' }">Отмена</router-link>
      </footer>
    </form>
  </section>
</template>

<script>
import { reactive, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import OrganizationApi from './js/organizationApi.js';
import { useToast } from 'vue-toastification';

export default {
  name: 'OrganizationForm',
  setup() {
    const router = useRouter();
    const saving = false;
    const toast = useToast();
    const form = reactive({
      name: '', slug: '', description: '',
      website: '', email: '', phone: '',
      country: '', timezone: '', address: '',
      industry: '',
      visibility: 'by_invite',
      default_role: 'member',
      status: 'active',
      billing_name: '', billing_vat: '', billing_address: ''
    });

    let slugTouched = false;
    watch(() => form.slug, () => { slugTouched = true; });
    watch(() => form.name, (val) => {
      if (!slugTouched) form.slug = (val || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
    });

    const canSubmit = computed(() => !!form.name && !!form.visibility && !!form.status);

    const save = async () => {
      // Клиентская защита от дублей имен (нормализация)
      try {
        const res = await OrganizationApi.getOrganizations();
        const list = res.data.results || res.data || [];
        const norm = (s) => (s || '').toString().trim().replace(/\s+/g,' ').toLowerCase();
        const exists = list.some(o => norm(o.name) === norm(form.name));
        if (exists) {
          toast.error('Организация с таким названием уже существует');
          return;
        }
      } catch (_) {}
      await OrganizationApi.createOrganization({ ...form });
      router.push({ name: 'OrganizationList' });
    };

    return { form, save, saving, canSubmit };
  }
};
</script>
