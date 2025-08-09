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
  const spacing = 180
  props.tasks.forEach((task, index) => {
    const nodeId = `task-${task.id}`
    nodes.value.push({
      id: nodeId,
      data: { label: task.title },
      position: { x: index * spacing, y: 150 },
      draggable: false
    })
    edges.value.push({
      id: `edge-${task.id}`,
      source: rootId,
      target: nodeId
    })
  })
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

