import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '../src/App.vue'
import LibraryView from '../src/views/LibraryView.vue'

describe('Ped-Agent shell', () => {
  it('opens the knowledge library and reserves future research areas', async () => {
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

    expect(wrapper.text()).toContain('知识库')
    expect(wrapper.text()).toContain('智能问答')
    expect(wrapper.text()).toContain('轨迹分析')
    expect(wrapper.text()).toContain('安全评估')
    expect(wrapper.text()).toContain('实验支持')
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
