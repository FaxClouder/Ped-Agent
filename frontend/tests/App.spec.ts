import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '../src/App.vue'
import LibraryView from '../src/views/LibraryView.vue'

describe('Ped-Agent shell', () => {
  it('separates foundation modules from derived research applications', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div>Library</div>' } },
        { path: '/qa', component: { template: '<div>Answer</div>' } },
      ],
    })
    await router.push('/')
    await router.isReady()
    const wrapper = mount(App, {
      global: { plugins: [router] },
    })

    const foundation = wrapper.get('[aria-label="基础模块"]')
    const applications = wrapper.get('[aria-label="研究应用"]')

    expect(foundation.findAll('[data-module]')).toHaveLength(3)
    expect(foundation.text()).toContain('知识与证据底座')
    expect(foundation.text()).toContain('检测追踪与流动分析')
    expect(foundation.text()).toContain('LLM 问答与会话')
    expect(applications.text()).toContain('场景诊断')
    expect(applications.text()).toContain('安全评估')
    expect(applications.text()).toContain('实验支持')
    expect(wrapper.find('[data-route="knowledge"]').classes()).toContain('active')
    expect(wrapper.find('[data-route="answer"]').attributes('href')).toBe('/qa')
  })

  it('shows the first-stage knowledge workspace structure', () => {
    const wrapper = mount(LibraryView)

    expect(wrapper.get('h2').text()).toBe('知识库')
    expect(wrapper.find('[data-area="filters"]').exists()).toBe(true)
    expect(wrapper.find('[data-area="search"]').exists()).toBe(true)
    expect(wrapper.find('[data-area="evidence"]').exists()).toBe(true)
  })
})
