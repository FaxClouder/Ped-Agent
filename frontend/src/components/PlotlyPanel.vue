<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  data: Array<Record<string, unknown>>
  layout?: Record<string, unknown>
}>()

const root = ref<HTMLElement | null>(null)
let plotly: (typeof import('plotly.js-dist-min'))['default'] | null = null

async function render() {
  if (!root.value) return
  plotly ??= (await import('plotly.js-dist-min')).default
  await plotly.react(
    root.value,
    props.data as never[],
    { autosize: true, margin: { l: 54, r: 24, t: 42, b: 54 }, ...props.layout } as never,
    { responsive: true, displaylogo: false },
  )
}

onMounted(render)
watch(() => [props.data, props.layout], render, { deep: true })
onBeforeUnmount(() => {
  if (root.value && plotly) plotly.purge(root.value)
})
</script>

<template>
  <div ref="root" class="plotly-panel" aria-label="交互分析图"></div>
</template>
