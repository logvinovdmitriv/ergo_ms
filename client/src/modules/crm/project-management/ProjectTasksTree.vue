<template>
  <div class="task-tree">
    <VueFlow :nodes="nodes" :edges="edges" fit-view :zoom-on-scroll="false" :nodes-connectable="false" :edges-connectable="false" />
  </div>
</template>

<script setup>
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import { ref, watch } from 'vue'
import { VueFlow } from '@vue-flow/core'

const props = defineProps({
  project: { type: Object, required: true },
  tasks: { type: Array, default: () => [] }
})

const nodes = ref([])
const edges = ref([])

function buildGraph() {
  const rootId = `project-${props.project.id}`
  nodes.value = [
    {
      id: rootId,
      data: { label: props.project.name },
      position: { x: 0, y: 0 },
      draggable: false,
      type: 'input'
    }
  ]
  edges.value = []

  const tasksByParent = {}
  props.tasks.forEach(task => {
    const parentId = task.parent || null
    if (!tasksByParent[parentId]) tasksByParent[parentId] = []
    tasksByParent[parentId].push(task)
  })

  const levelSpacing = 150
  const nodeSpacing = 180

  function addChildren(parentId, tasks, depth, startX) {
    tasks.forEach((task, index) => {
      const nodeId = `task-${task.id}`
      const x = startX + index * nodeSpacing
      const y = depth * levelSpacing
      nodes.value.push({
        id: nodeId,
        data: { label: task.title },
        position: { x, y },
        draggable: false
      })
      edges.value.push({
        id: `edge-${parentId || 'root'}-${task.id}`,
        source: parentId ? `task-${parentId}` : rootId,
        target: nodeId
      })
      const children = tasksByParent[task.id]
      if (children && children.length) {
        addChildren(task.id, children, depth + 1, x)
      }
    })
  }

  addChildren(null, tasksByParent[null] || [], 1, 0)
}

watch(() => props.tasks, buildGraph, { immediate: true })
watch(() => props.project, buildGraph)
</script>

<style scoped>
.task-tree {
  width: 100%;
  height: 100%;
}
</style>

