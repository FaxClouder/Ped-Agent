<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

const moduleNavigation = [
  {
    index: '01',
    key: 'knowledge',
    name: '知识与证据底座',
    description: '文献、法规、正式证据与检索',
    route: '/',
    routeName: 'knowledge',
    stage: '建设中',
  },
  {
    index: '02',
    key: 'analysis',
    name: '检测追踪与流动分析',
    description: '视频、轨迹、指标与 Flow Evidence',
    stage: '工程骨架',
  },
  {
    index: '03',
    key: 'answer',
    name: 'LLM 问答与会话',
    description: '证据编排、验证回答与会话',
    route: '/qa',
    routeName: 'answer',
    stage: '可用',
  },
]

const researchApplications = [
  { name: '场景诊断', description: '组合正式证据与 Flow Evidence' },
  { name: '安全评估', description: '风险指标与规范符合性' },
  { name: '实验支持', description: '方案、数据与指标设计' },
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

      <nav class="primary-nav" aria-label="Ped-Agent 功能导航">
        <section class="nav-group" aria-label="基础模块">
          <p class="nav-group-title">基础模块</p>
          <RouterLink
            v-for="item in moduleNavigation"
            :key="item.key"
            :to="item.route || '#'"
            :data-module="item.key"
            :data-route="item.routeName"
            :class="['nav-item', { disabled: !item.route }]"
            active-class="active"
            :aria-disabled="!item.route"
            :tabindex="item.route ? 0 : -1"
            @click="!item.route && $event.preventDefault()"
          >
            <span class="nav-index">{{ item.index }}</span>
            <span class="nav-copy">
              <strong>{{ item.name }}</strong>
              <small>{{ item.description }}</small>
            </span>
            <span class="nav-stage">{{ item.stage }}</span>
          </RouterLink>
        </section>

        <section class="nav-group application-group" aria-label="研究应用">
          <p class="nav-group-title">研究应用</p>
          <div
            v-for="item in researchApplications"
            :key="item.name"
            class="nav-item application-item disabled"
            data-application
            aria-disabled="true"
          >
            <span class="nav-index">—</span>
            <span class="nav-copy">
              <strong>{{ item.name }}</strong>
              <small>{{ item.description }}</small>
            </span>
            <span class="nav-stage">后续</span>
          </div>
        </section>
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
