import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import App from '../src/App.vue'
import LibraryView from '../src/views/LibraryView.vue'

describe('Ped-Agent shell', () => {
  it('opens the knowledge library and reserves future research areas', () => {
    const wrapper = mount(App, {
      global: { stubs: { RouterView: { template: '<div>Library</div>' } } },
    })

    expect(wrapper.text()).toContain('知识库')
    expect(wrapper.text()).toContain('智能问答')
    expect(wrapper.text()).toContain('轨迹分析')
    expect(wrapper.text()).toContain('安全评估')
    expect(wrapper.text()).toContain('实验支持')
    expect(wrapper.find('[data-route="knowledge"]').classes()).toContain('active')
  })

  it('shows the first-stage knowledge workspace structure', () => {
    const wrapper = mount(LibraryView)

    expect(wrapper.get('h2').text()).toBe('知识库')
    expect(wrapper.find('[data-area="filters"]').exists()).toBe(true)
    expect(wrapper.find('[data-area="search"]').exists()).toBe(true)
    expect(wrapper.find('[data-area="evidence"]').exists()).toBe(true)
  })
})
