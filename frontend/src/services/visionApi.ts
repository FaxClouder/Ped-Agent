export interface VisionModelSummary {
  model_id: string
  name: string
  version?: string
  available: boolean
  input_size?: number
  error?: string | null
}

export interface SceneSummary {
  scene_id: string
  version: number
  name: string
  resolution?: [number, number]
}

export interface VisionTask {
  id: string
  task_name: string
  status: string
  model_id: string
  scene_id?: string | null
  error?: string | null
  updated_at?: string
}

export interface VisionTaskCreated {
  task_id: string
  status: string
  events_url: string
}

export interface CharucoIntrinsics {
  camera_matrix: number[][]
  distortion: number[]
  image_size: [number, number]
  rms_reprojection_error_px: number
  valid_view_count: number
}

export interface VisionResults {
  task: VisionTask
  physical_metrics_available: boolean
  calibration: Record<string, unknown> | null
  analysis: Record<string, any> | null
  artifacts: Array<Record<string, unknown>>
  review_queue?: Array<Record<string, any>>
  track_summary?: Array<Record<string, any>>
}

async function requestJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  if (init?.body && !(init.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  const response = await fetch(input, { ...init, headers })
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string }
    throw new Error(body.detail ?? `请求失败 (${response.status})`)
  }
  return (await response.json()) as T
}

export const visionApi = {
  listModels: () => requestJson<VisionModelSummary[]>('/api/vision/models'),
  listScenes: () => requestJson<SceneSummary[]>('/api/vision/scenes'),
  listTasks: () => requestJson<VisionTask[]>('/api/vision/tasks'),
  createSceneFromPixelGeometry: (payload: Record<string, unknown>) =>
    requestJson<SceneSummary>('/api/vision/scenes/from-pixel-geometry', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  calibrateCharuco: (payload: {
    images: File[]
    squaresX: number
    squaresY: number
    squareLengthM: number
    markerLengthM: number
    dictionaryId: number
    minimumViews: number
    minimumCornersPerView: number
  }) => {
    const form = new FormData()
    for (const image of payload.images) form.append('images', image)
    form.set('squares_x', String(payload.squaresX))
    form.set('squares_y', String(payload.squaresY))
    form.set('square_length_m', String(payload.squareLengthM))
    form.set('marker_length_m', String(payload.markerLengthM))
    form.set('dictionary_id', String(payload.dictionaryId))
    form.set('minimum_views', String(payload.minimumViews))
    form.set('minimum_corners_per_view', String(payload.minimumCornersPerView))
    return requestJson<CharucoIntrinsics>('/api/vision/scenes/calibrate/charuco', {
      method: 'POST',
      body: form,
    })
  },
  watchEvents: (taskId: string, onEvent: EventListener): EventSource | null => {
    if (typeof EventSource === 'undefined') return null
    const source = new EventSource(`/api/vision/tasks/${taskId}/events`)
    for (const eventName of ['status', 'artifact', 'error', 'retry', 'artifacts_invalidated']) {
      source.addEventListener(eventName, onEvent)
    }
    return source
  },
  createTask: (payload: {
    taskName: string
    modelId: string
    sceneId?: string
    video: File
  }) => {
    const form = new FormData()
    form.set('task_name', payload.taskName)
    form.set('model_id', payload.modelId)
    if (payload.sceneId) form.set('scene_id', payload.sceneId)
    form.set('video', payload.video)
    return requestJson<VisionTaskCreated>('/api/vision/tasks', { method: 'POST', body: form })
  },
  getResults: (taskId: string) =>
    requestJson<VisionResults>(`/api/vision/tasks/${taskId}/results`),
  submitReview: (taskId: string, patch: Record<string, unknown>) =>
    requestJson<Record<string, unknown>>(`/api/vision/tasks/${taskId}/review`, {
      method: 'POST',
      body: JSON.stringify(patch),
    }),
  submitCalibration: (taskId: string, report: Record<string, unknown>) =>
    requestJson<Record<string, unknown>>(`/api/vision/tasks/${taskId}/calibration`, {
      method: 'POST',
      body: JSON.stringify(report),
    }),
  rerun: (taskId: string, fromStage: string) =>
    requestJson<Record<string, unknown>>(`/api/vision/tasks/${taskId}/rerun`, {
      method: 'POST',
      body: JSON.stringify({ from_stage: fromStage }),
    }),
  cancel: (taskId: string) =>
    requestJson<Record<string, unknown>>(`/api/vision/tasks/${taskId}/cancel`, {
      method: 'POST',
    }),
  listExports: (taskId: string) =>
    requestJson<Array<Record<string, unknown>>>(`/api/vision/tasks/${taskId}/exports`),
}
