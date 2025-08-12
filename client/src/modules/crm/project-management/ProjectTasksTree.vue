<template>
  <div class="task-tree">
    <div class="task-tree-header">
      <h4>Дерево задач проекта</h4>
      <div class="task-tree-controls">
        <input class="form-control form-control-sm filter-input" v-model.trim="filterQuery" placeholder="Поиск по названию" />
        <button @click="expandAll" class="btn btn-sm btn-outline-primary">Развернуть все</button>
        <button @click="collapseAll" class="btn btn-sm btn-outline-secondary">Свернуть все</button>
      </div>
    </div>
    <div v-if="breadcrumbs.length" class="task-tree-breadcrumbs">
      <span v-for="(crumb, idx) in breadcrumbs" :key="`bc-${crumb.id}`" class="crumb" @click="focusCrumb(idx)">
        {{ crumb.title }}<span v-if="idx<breadcrumbs.length-1"> / </span>
      </span>
    </div>
    
    <div class="task-tree-content">
      <VueFlow 
        :nodes="nodes" 
        :edges="edges" 
        fit-view 
        :zoom-on-scroll="true" 
        :nodes-connectable="false" 
        :edges-connectable="false"
        :min-zoom="0.5"
        :max-zoom="2"
        class="task-flow"
        @node-click="onNodeClick"
      />
    </div>
  </div>
</template>

<script setup>
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import { ref, watch, computed, onMounted } from 'vue'
import { VueFlow } from '@vue-flow/core'
import projectManagementApi from '@/modules/crm/project-management/js/projectManagementApi.js'

const props = defineProps({
  project: { type: Object, required: true },
  tasks: { type: Array, default: () => [] }
})

const nodes = ref([])
const edges = ref([])
const expandedNodes = ref(new Set())
const lazyChildrenCache = new Map()
const allTasks = ref([])
const filterQuery = ref('')
const breadcrumbs = ref([])

// Набор видимых задач с учётом раскрытия и фильтра
const filteredTasks = computed(() => {
  const q = (filterQuery.value || '').toLowerCase()
  if (!q) {
    // поведение как раньше — видимы корни и раскрытые ветки
    return allTasks.value.filter(task => {
      if (expandedNodes.value.has(task.id) || !task.parent) return true
      let p = task.parent
      while (p) {
        if (expandedNodes.value.has(p)) return true
        const pt = allTasks.value.find(t => t.id === p)
        p = pt ? pt.parent : null
      }
      return false
    })
  }
  // При поиске: видимы совпадения и их предки/потомки
  const match = (t) => (t.title || '').toLowerCase().includes(q)
  const idToTask = new Map(allTasks.value.map(t => [t.id, t]))
  const visibleIds = new Set()
  // отмечаем совпадения и предков
  allTasks.value.forEach(t => {
    if (match(t)) {
      let cur = t
      while (cur) {
        visibleIds.add(cur.id)
        cur = cur.parent ? idToTask.get(cur.parent) : null
      }
    }
  })
  // отмечаем детей совпавших при раскрытии
  const addDescendants = (id) => {
    allTasks.value.forEach(t => {
      if (t.parent === id) {
        visibleIds.add(t.id)
        addDescendants(t.id)
      }
    })
  }
  Array.from(visibleIds).forEach(id => addDescendants(id))
  return allTasks.value.filter(t => visibleIds.has(t.id))
})

async function ensureChildrenLoaded(taskId) {
  if (!taskId) return
  if (lazyChildrenCache.has(taskId)) return
  try {
    const res = await projectManagementApi.client.get('/crm/tasks/project_tree/', {
      params: { project_id: props.project.id, root_id: taskId, depth: 1 }
    })
    const tree = res.data?.tree || []
    const children = Array.isArray(tree) ? tree : []
    lazyChildrenCache.set(taskId, children)
    const existing = new Set(allTasks.value.map(t => t.id))
    const merged = [...allTasks.value]
    children.forEach(c => { if (!existing.has(c.id)) merged.push(c) })
    allTasks.value = merged
  } catch (e) {
    // ignore
  }
}

async function buildGraph() {
  const rootId = `project-${props.project.id}`
  nodes.value = [
    {
      id: rootId,
      data: { 
        label: props.project.name,
        type: 'project',
        project: props.project
      },
      position: { x: 0, y: 0 },
      draggable: false,
      type: 'input',
      style: {
        background: 'var(--bs-primary)',
        color: 'white',
        border: '2px solid var(--bs-primary)',
        borderRadius: '8px',
        padding: '10px',
        fontSize: '14px',
        fontWeight: 'bold'
      }
    }
  ]
  edges.value = []

  const tasksByParent = {}
  filteredTasks.value.forEach(task => {
    const parentId = task.parent || null
    if (!tasksByParent[parentId]) tasksByParent[parentId] = []
    tasksByParent[parentId].push(task)
  })

  const levelSpacing = 120
  const nodeSpacing = 200

  async function addChildren(parentId, tasks, depth, startX) {
    for (let index = 0; index < tasks.length; index++) {
      const task = tasks[index]
      const nodeId = `task-${task.id}`
      const x = startX + index * nodeSpacing
      const y = depth * levelSpacing
      
      // Определяем стиль узла в зависимости от статуса и приоритета
      const nodeStyle = getTaskNodeStyle(task)
      
      const isMatch = (task.title || '').toLowerCase().includes((filterQuery.value||'').toLowerCase())
      nodes.value.push({
        id: nodeId,
        data: { 
          label: task.title,
          type: 'task',
          task: task,
          hasSubtasks: task.subtasks && task.subtasks.length > 0,
          subtasksCount: task.subtasks_count || 0
        },
        position: { x, y },
        draggable: false,
        style: isMatch ? { ...nodeStyle, boxShadow: '0 0 0 3px rgba(13,110,253,0.5)' } : nodeStyle
      })
      
      // Добавляем ребро
      edges.value.push({
        id: `edge-${parentId || 'root'}-${task.id}`,
        source: parentId ? `task-${parentId}` : rootId,
        target: nodeId,
        style: { stroke: 'var(--bs-border-color)', strokeWidth: 2 }
      })
      
      // Рекурсивно добавляем подзадачи
      let children = tasksByParent[task.id]
      if ((!children || !children.length) && expandedNodes.value.has(task.id)) {
        await ensureChildrenLoaded(task.id)
        children = lazyChildrenCache.get(task.id)
        if (children && children.length) {
          tasksByParent[task.id] = children
        }
      }
      if (children && children.length) {
        await addChildren(task.id, children, depth + 1, x)
      }
    }
  }

  addChildren(null, tasksByParent[null] || [], 1, 0)
}

// Раскрыть путь в дереве до задачи по списку ID (от корня к листу)
async function expandPathTo(pathIds = []) {
  try {
    for (const id of pathIds) {
      expandedNodes.value.add(id)
      await ensureChildrenLoaded(id)
    }
    await buildGraph()
  } catch (e) {
    // ignore
  }
}

function getTaskNodeStyle(task) {
  const baseStyle = {
    border: '2px solid var(--bs-border-color)',
    borderRadius: '8px',
    padding: '12px',
    fontSize: '12px',
    fontWeight: '500',
    minWidth: '150px',
    textAlign: 'center'
  }
  
  // Цвета из палитры Bootstrap
  const statusColors = {
    'todo': 'var(--bs-secondary)',
    'in_progress': 'var(--bs-warning)',
    'review': 'var(--bs-info)',
    'done': 'var(--bs-success)',
    'cancelled': 'var(--bs-danger)'
  }
  const priorityBorders = {
    'low': 'var(--bs-secondary)',
    'medium': 'var(--bs-primary)',
    'high': 'var(--bs-warning)',
    'urgent': 'var(--bs-danger)'
  }
  
  const statusColor = statusColors[task.status] || 'var(--bs-secondary)'
  const priorityColor = priorityBorders[task.priority] || 'var(--bs-secondary)'
  const now = new Date()
  const isOverdue = task.due_date && new Date(task.due_date) < now && task.status !== 'done'
  
  return {
    ...baseStyle,
    background: statusColor,
    color: 'white',
    borderColor: isOverdue ? 'var(--bs-danger)' : priorityColor
  }
}

function expandAll() {
  allTasks.value.forEach(task => { expandedNodes.value.add(task.id) })
  buildGraph()
}

function collapseAll() {
  expandedNodes.value.clear()
  buildGraph()
}

async function toggleNode(nodeId) {
  if (expandedNodes.value.has(nodeId)) {
    expandedNodes.value.delete(nodeId)
  } else {
    expandedNodes.value.add(nodeId)
  }
  await buildGraph()
}

// Синхронизируем локальную копию задач и пересобираем граф
watch(() => props.tasks, (val) => { allTasks.value = Array.isArray(val) ? [...val] : [] }, { immediate: true, deep: true })
watch(() => [allTasks.value, props.project], buildGraph, { immediate: true, deep: true })

// Экспортируем метод для родителя (для навигации к задаче)
defineExpose({ expandPathTo })

// Слушаем изменения в развернутых узлах
watch(expandedNodes, buildGraph, { deep: true })

function onNodeClick(event) {
  try {
    const node = event?.node || {}
    const idStr = node?.id || ''
    const match = idStr.match(/^task-(\d+)$/)
    if (!match) return
    const taskId = Number(match[1])
    // собираем хлебные крошки
    const idToTask = new Map(allTasks.value.map(t => [t.id, t]))
    const chain = []
    let cur = idToTask.get(taskId)
    while (cur) {
      chain.unshift({ id: cur.id, title: cur.title })
      cur = cur.parent ? idToTask.get(cur.parent) : null
    }
    breadcrumbs.value = chain
  } catch {}
}

function focusCrumb(index) {
  const path = breadcrumbs.value.slice(0, index + 1).map(c => c.id)
  expandPathTo(path)
}

// Сохраняем состояние раскрытия по проекту
const storageKey = computed(() => `tree-expanded-${props.project?.id}`)
watch(expandedNodes, (val) => {
  try {
    const arr = Array.from(val.values())
    localStorage.setItem(storageKey.value, JSON.stringify(arr))
  } catch {}
}, { deep: true })

onMounted(() => {
  try {
    const raw = localStorage.getItem(storageKey.value)
    if (raw) {
      const arr = JSON.parse(raw)
      if (Array.isArray(arr)) {
        expandedNodes.value = new Set(arr)
      }
    }
  } catch {}
})
</script>

<style scoped>
.task-tree {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.task-tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
}

.task-tree-header h4 {
  margin: 0;
  color: #495057;
}

.task-tree-controls {
  display: flex;
  gap: 10px;
}

.task-tree-content {
  flex: 1;
  position: relative;
}

.task-flow {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

:deep(.vue-flow__node) {
  cursor: pointer;
  transition: all 0.2s ease;
}

:deep(.vue-flow__node:hover) {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

:deep(.vue-flow__edge) {
  transition: all 0.2s ease;
}

:deep(.vue-flow__edge:hover) {
  stroke-width: 3px;
}

:deep(.vue-flow__controls) {
  position: absolute;
  top: 10px;
  right: 10px;
}

:deep(.vue-flow__minimap) {
  position: absolute;
  bottom: 10px;
  right: 10px;
}
</style>

