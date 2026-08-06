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
        { path: '/vision', component: { template: '<div>Vision</div>' } },
      ],
    })
    await router.push('/')
    await router.isReady()
    const wrapper = mount(App, {
      global: { plugins: [router] },
    })

    const foundation = wrapper.get('[aria-label="基础模块"]')
    const applications = wrapper.get('[aria-label="研究应用"]')
    const analysis = foundation.get('[data-module="analysis"]')
    const applicationEntries = applications.findAll('[data-application]')

    expect(foundation.findAll('[data-module]')).toHaveLength(3)
    expect(foundation.findAll('a[data-module]')).toHaveLength(3)
    expect(foundation.text()).toContain('知识与证据底座')
    expect(foundation.text()).toContain('检测追踪与流动分析')
    expect(foundation.text()).toContain('LLM 问答与会话')
    expect(applications.text()).toContain('场景诊断')
    expect(applications.text()).toContain('安全评估')
    expect(applications.text()).toContain('实验支持')
    expect(analysis.attributes('href')).toBe('/vision')
    expect(analysis.attributes('role')).toBeUndefined()
    expect(analysis.attributes('aria-disabled')).toBeUndefined()
    expect(analysis.classes()).not.toContain('active')
    expect(applicationEntries).toHaveLength(3)
    for (const application of applicationEntries) {
      expect(application.attributes('href')).toBeUndefined()
      expect(application.attributes('role')).toBe('link')
      expect(application.attributes('aria-disabled')).toBe('true')
      expect(application.attributes('tabindex')).toBeUndefined()
    }
    expect(wrapper.find('[data-route="knowledge"]').classes()).toContain('active')
    expect(wrapper.find('[data-route="answer"]').attributes('href')).toBe('/qa')
    expect(wrapper.find('[data-route="vision"]').attributes('href')).toBe('/vision')
  })

  it('keeps answer active while analysis remains available', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div>Library</div>' } },
        { path: '/qa', component: { template: '<div>Answer</div>' } },
        { path: '/vision', component: { template: '<div>Vision</div>' } },
      ],
    })
    await router.push('/qa')
    await router.isReady()
    const wrapper = mount(App, {
      global: { plugins: [router] },
    })

    const analysis = wrapper.get('[data-module="analysis"]')
    const answer = wrapper.get('[data-route="answer"]')

    expect(answer.classes()).toContain('active')
    expect(answer.attributes('href')).toBe('/qa')
    expect(analysis.classes()).not.toContain('active')
    expect(analysis.attributes('href')).toBe('/vision')
    expect(analysis.attributes('aria-disabled')).toBeUndefined()
  })

  it('activates detection tracking and flow analysis on the vision route', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div>Library</div>' } },
        { path: '/qa', component: { template: '<div>Answer</div>' } },
        { path: '/vision', component: { template: '<div>Vision</div>' } },
      ],
    })
    await router.push('/vision')
    await router.isReady()
    const wrapper = mount(App, {
      global: { plugins: [router] },
    })

    const analysis = wrapper.get('[data-module="analysis"]')

    expect(analysis.classes()).toContain('active')
    expect(analysis.attributes('href')).toBe('/vision')
    expect(wrapper.get('[data-route="knowledge"]').classes()).not.toContain('active')
    expect(wrapper.get('[data-route="answer"]').classes()).not.toContain('active')
  })

  it('shows the first-stage knowledge workspace structure', () => {
    const wrapper = mount(LibraryView)

    expect(wrapper.get('h2').text()).toBe('知识库')
    expect(wrapper.find('[data-area="filters"]').exists()).toBe(true)
    expect(wrapper.find('[data-area="search"]').exists()).toBe(true)
    expect(wrapper.find('[data-area="evidence"]').exists()).toBe(true)
  })
})
