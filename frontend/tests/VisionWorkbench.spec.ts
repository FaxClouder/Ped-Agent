import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import VisionWorkbenchView from '../src/views/VisionWorkbenchView.vue'


const response = (body: unknown, status = 200) =>
  Promise.resolve(
    new Response(JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  )

afterEach(() => {
  vi.unstubAllGlobals()
})

class FakeEventSource {
  static instances: FakeEventSource[] = []
  listeners = new Map<string, EventListener>()
  closed = false

  constructor(public url: string) {
    FakeEventSource.instances.push(this)
  }

  addEventListener(name: string, listener: EventListener) {
    this.listeners.set(name, listener)
  }

  emit(name: string) {
    this.listeners.get(name)?.(new Event(name))
  }

  close() {
    this.closed = true
  }
}

describe('Vision trajectory workbench', () => {
  it('loads resources and exposes the six result perspectives', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)
        if (url.endsWith('/models')) {
          return response([
            {
              model_id: 'mixed-flow-v1',
              name: 'Mixed Flow',
              version: '1',
              available: true,
              input_size: 1280,
            },
          ])
        }
        if (url.endsWith('/scenes')) {
          return response([{ scene_id: 'scene-1', version: 1, name: 'Station' }])
        }
        return response([])
      }),
    )

    const wrapper = mount(VisionWorkbenchView, {
      global: { stubs: { PlotlyPanel: true } },
    })
    await flushPromises()

    expect(wrapper.get('h2').text()).toContain('视觉轨迹')
    expect(wrapper.findAll('[data-result-tab]').map((item) => item.text())).toEqual([
      '质量',
      '个体',
      '流量',
      '空间',
      'OD',
      '交互',
    ])
    expect(wrapper.find('option[value="mixed-flow-v1"]').exists()).toBe(true)
    expect(wrapper.find('option[value="scene-1"]').exists()).toBe(true)
    expect(wrapper.find('[data-area="calibration-wizard"]').exists()).toBe(true)
    expect(wrapper.find('[data-area="review-editor"]').exists()).toBe(true)
  })

  it('uploads one video task as multipart form data', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)
      if (url.endsWith('/models')) {
        return response([{ model_id: 'mixed-flow-v1', name: 'Mixed', available: true }])
      }
      if (url.endsWith('/scenes')) {
        return response([{ scene_id: 'scene-1', version: 1, name: 'Scene' }])
      }
      if (url.endsWith('/tasks') && init?.method === 'POST') {
        expect(init.body).toBeInstanceOf(FormData)
        const form = init.body as FormData
        expect(form.get('task_name')).toBe('Morning flow')
        expect(form.get('model_id')).toBe('mixed-flow-v1')
        expect((form.get('video') as File).name).toBe('flow.mp4')
        return response({ task_id: 'task-1', status: 'queued', events_url: '/events' }, 202)
      }
      return response([])
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(VisionWorkbenchView, {
      global: { stubs: { PlotlyPanel: true } },
    })
    await flushPromises()
    await wrapper.get('[name="task_name"]').setValue('Morning flow')
    await wrapper.get('[name="model_id"]').setValue('mixed-flow-v1')
    await wrapper.get('[name="scene_id"]').setValue('scene-1')
    const input = wrapper.get('input[type="file"]')
    Object.defineProperty(input.element, 'files', {
      value: [new File(['video'], 'flow.mp4', { type: 'video/mp4' })],
    })
    await input.trigger('change')

    await wrapper.get('form[data-area="task-create"]').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('task-1')
  })

  it('refreshes the selected task when an SSE status event arrives', async () => {
    FakeEventSource.instances = []
    vi.stubGlobal('EventSource', FakeEventSource)
    let taskStatus = 'analysis_running'
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)
        if (url.endsWith('/models')) return response([])
        if (url.endsWith('/scenes')) return response([])
        if (url.endsWith('/tasks')) {
          return response([{ id: 'task-1', task_name: 'Flow', status: taskStatus, model_id: 'm1' }])
        }
        if (url.endsWith('/tasks/task-1/results')) {
          return response({
            task: { id: 'task-1', task_name: 'Flow', status: taskStatus, model_id: 'm1' },
            physical_metrics_available: taskStatus === 'completed',
            calibration: null,
            analysis: null,
            artifacts: [],
          })
        }
        return response({})
      }),
    )
    const wrapper = mount(VisionWorkbenchView, {
      global: { stubs: { PlotlyPanel: true } },
    })
    await flushPromises()

    await wrapper.get('.task-row').trigger('click')
    await flushPromises()
    expect(FakeEventSource.instances[0]?.url).toBe('/api/vision/tasks/task-1/events')

    taskStatus = 'completed'
    FakeEventSource.instances[0].emit('status')
    await flushPromises()

    expect(wrapper.get('.task-row em').text()).toBe('completed')
    wrapper.unmount()
    expect(FakeEventSource.instances[0].closed).toBe(true)
  })

  it('stages drawn ROI pixels and saves a new SceneProfile version', async () => {
    let savedScene: any = null
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        if (url.endsWith('/models') || url.endsWith('/tasks')) return response([])
        if (url.endsWith('/scenes/from-pixel-geometry')) {
          savedScene = JSON.parse(String(init?.body))
          return response({ ...savedScene, path: 'scene.json' }, 201)
        }
        if (url.endsWith('/scenes')) return response([])
        return response({})
      }),
    )
    const wrapper = mount(VisionWorkbenchView, {
      global: { stubs: { PlotlyPanel: true } },
    })
    await flushPromises()
    await wrapper.get('[name="scene_profile_id"]').setValue('station-east')
    await wrapper.get('[name="scene_profile_name"]').setValue('Station east')
    await wrapper.get('[name="camera_fingerprint"]').setValue('cam-east-001')
    await wrapper.get('[name="scene_width"]').setValue('1000')
    await wrapper.get('[name="scene_height"]').setValue('500')
    const canvas = wrapper.get('.video-stage svg')
    vi.spyOn(canvas.element, 'getBoundingClientRect').mockReturnValue({
      left: 0,
      top: 0,
      width: 100,
      height: 100,
      right: 100,
      bottom: 100,
      x: 0,
      y: 0,
      toJSON: () => ({}),
    })
    for (const [clientX, clientY] of [[0, 0], [100, 0], [100, 100], [0, 100]]) {
      await canvas.trigger('click', { clientX, clientY })
    }
    await wrapper.get('[data-action="stage-geometry"]').trigger('click')
    await wrapper.get('[data-action="save-scene"]').trigger('click')
    await flushPromises()

    expect(savedScene?.scene_id).toBe('station-east')
    expect(savedScene?.roi).toEqual([[0, 0], [1000, 0], [1000, 500], [0, 500]])
    expect(savedScene?.calibration_report.scene_id).toBe('station-east')
  })

  it('submits relabel, delete, split, merge, and move as review operation choices', async () => {
    let reviewPatch: any = null
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        if (url.endsWith('/models') || url.endsWith('/scenes')) return response([])
        if (url.endsWith('/tasks')) {
          return response([{ id: 'task-1', task_name: 'Flow', status: 'awaiting_review', model_id: 'm1' }])
        }
        if (url.endsWith('/tasks/task-1/results')) {
          return response({
            task: { id: 'task-1', task_name: 'Flow', status: 'awaiting_review', model_id: 'm1' },
            physical_metrics_available: false,
            calibration: null,
            analysis: null,
            artifacts: [{ artifact_id: 'pixel-1', artifact_type: 'pixel_tracks' }],
          })
        }
        if (url.endsWith('/tasks/task-1/review')) {
          reviewPatch = JSON.parse(String(init?.body))
          return response({ status: 'awaiting_calibration' }, 201)
        }
        return response({})
      }),
    )
    const wrapper = mount(VisionWorkbenchView, {
      global: { stubs: { PlotlyPanel: true } },
    })
    await flushPromises()
    await wrapper.get('.task-row').trigger('click')
    await flushPromises()
    const operationSelect = wrapper.get('[name="review_operation"]')
    expect(operationSelect.findAll('option').map((item) => item.attributes('value'))).toEqual([
      'move_point',
      'delete_track',
      'relabel_track',
      'split_track',
      'merge_tracks',
    ])
    await operationSelect.setValue('relabel_track')
    await wrapper.get('[name="review_track_id"]').setValue('7')
    await wrapper.get('[name="review_semantic_class"]').setValue('pedestrian_umbrella')
    await wrapper.get('[data-action="add-review-operation"]').trigger('click')
    await wrapper.get('form.review-form').trigger('submit')
    await flushPromises()

    expect(reviewPatch?.operations).toEqual([{
      operation: 'relabel_track',
      track_id: 7,
      semantic_class: 'pedestrian_umbrella',
    }])
  })

  it('uploads multiple ChArUco views and displays the intrinsics result', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input)
        if (url.endsWith('/models') || url.endsWith('/scenes') || url.endsWith('/tasks')) {
          return response([])
        }
        if (url.endsWith('/scenes/calibrate/charuco')) {
          const form = init?.body as FormData
          expect(form.getAll('images')).toHaveLength(3)
          expect(form.get('squares_x')).toBe('7')
          return response({
            camera_matrix: [[1000, 0, 320], [0, 1000, 240], [0, 0, 1]],
            distortion: [0.1, -0.05, 0, 0, 0],
            image_size: [640, 480],
            rms_reprojection_error_px: 0.3,
            valid_view_count: 5,
          })
        }
        return response({})
      }),
    )
    const wrapper = mount(VisionWorkbenchView, {
      global: { stubs: { PlotlyPanel: true } },
    })
    await flushPromises()
    const input = wrapper.get('input[name="charuco_images"]')
    Object.defineProperty(input.element, 'files', {
      value: [0, 1, 2].map((index) => new File(['image'], `view-${index}.png`, { type: 'image/png' })),
    })
    await input.trigger('change')
    await wrapper.get('[data-action="calibrate-charuco"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-area="charuco-result"]').text()).toContain('5 个有效视角')
  })
})
