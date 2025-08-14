<!-- client/src/modules/crm/organizations/components/TransferOwnershipModal.vue -->
<template>
  <teleport to="body">
    <div class="modal-backdrop" @click.self="close">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Передать владение</h3>
          <button class="icon-btn" @click="close" aria-label="Закрыть">×</button>
        </div>

        <div class="modal-body">
          <p class="hint">
            Вы владелец организации. Чтобы выйти, выберите нового владельца.
          </p>

          <label class="field">
            <span>Новый владелец</span>
            <select v-model="selected">
              <option disabled value="">— выберите участника —</option>
              <option v-for="m in eligible" :key="m.user.id" :value="m.user.id">
                {{ m.user.full_name || m.user.email }} — {{ m.role }}
              </option>
            </select>
          </label>
        </div>

        <div class="modal-footer">
          <button class="btn" :disabled="!selected" @click="submit">Передать</button>
          <button class="btn btn--ghost" @click="close">Отмена</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  members: { type: Array, required: true },
  currentOwnerId: { type: [String, Number], required: true },
});
const emit = defineEmits(['close', 'submit']);

const selected = ref('');
const eligible = computed(() =>
  (props.members || []).filter(
    (m) => String(m.user?.id) !== String(props.currentOwnerId) && m.status === 'accepted'
  )
);

function close() { emit('close'); }
function submit() { emit('submit', { newOwnerId: selected.value }); }
</script>

<style scoped>
.modal-backdrop { position: fixed; inset:0; background: rgba(0,0,0,.45);
  display:flex; align-items:center; justify-content:center; z-index: 2000; }
.modal-card { width:520px; max-width:calc(100vw - 32px); background: var(--c-surface, #111);
  border:1px solid rgba(255,255,255,.08); border-radius:12px; box-shadow:0 12px 36px rgba(0,0,0,.4); }
.modal-header, .modal-footer { padding: 16px 20px; display:flex; align-items:center; }
.modal-header { justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,.06); }
.modal-body { padding: 16px 20px; display:grid; gap: 12px; }
.field { display: grid; gap: 6px; }
.field select { padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,.1); background: transparent; color: inherit; }
.hint { opacity: .8; margin: 0 0 6px; }
.btn { padding:10px 14px; border-radius:8px; border:1px solid rgba(255,255,255,.1); }
.btn--ghost { background: transparent; }
.icon-btn { font-size: 20px; width: 32px; height: 32px; border-radius: 8px; }
</style>
