<script setup lang="ts">
import { RouterView } from 'vue-router'

const navigation = [
  { name: '知识库', description: '文献、法规与原文证据', active: true },
  { name: '智能问答', description: '基于证据的研究问答', active: false },
  { name: '轨迹分析', description: '轨迹指标与场景诊断', active: false },
  { name: '安全评估', description: '风险与规范符合性', active: false },
  { name: '实验支持', description: '方案与指标设计', active: false },
]
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar" aria-label="Ped-Agent 研究模块导航">
      <header class="brand-block">
        <p class="brand-kicker">Pedestrian research agent</p>
        <h1>Ped-Agent</h1>
        <p class="brand-summary">以可追溯原文为基础的行人流研究工作台。</p>
      </header>

      <nav class="primary-nav" aria-label="主要功能">
        <button
          v-for="(item, index) in navigation"
          :key="item.name"
          type="button"
          :disabled="!item.active"
          :data-route="item.active ? 'knowledge' : undefined"
          :class="['nav-item', { active: item.active }]"
        >
          <span class="nav-index">0{{ index + 1 }}</span>
          <span class="nav-copy">
            <strong>{{ item.name }}</strong>
            <small>{{ item.description }}</small>
          </span>
          <span class="nav-stage">{{ item.active ? '阶段 1' : '后续' }}</span>
        </button>
      </nav>

      <footer class="sidebar-footer">
        <span>Local-first</span>
        <span>Evidence-bound</span>
      </footer>
    </aside>

    <main class="main-canvas">
      <RouterView />
    </main>
  </div>
</template>
