<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import PlotlyPanel from '../components/PlotlyPanel.vue'
import {
  type CharucoIntrinsics,
  type SceneSummary,
  type VisionModelSummary,
  type VisionResults,
  type VisionTask,
  visionApi,
} from '../services/visionApi'

type NormalizedPoint = { x: number; y: number }
type PixelPoint = [number, number]
type ReviewOperation = Record<string, unknown>

const models = ref<VisionModelSummary[]>([])
const scenes = ref<SceneSummary[]>([])
const tasks = ref<VisionTask[]>([])
const results = ref<VisionResults | null>(null)
const selectedTaskId = ref('')
const taskName = ref('')
const modelId = ref('')
const sceneId = ref('')
const videoFile = ref<File | null>(null)
const videoPreview = ref('')
const submitting = ref(false)
const error = ref('')
const activeResultTab = ref('质量')
const geometryMode = ref('roi')
const geometryName = ref('area-1')
const geometryPoints = ref<NormalizedPoint[]>([])
const storedGeometry = ref({
  roi: [] as NormalizedPoint[],
  exclusion_zones: {} as Record<string, NormalizedPoint[]>,
  zones: {} as Record<string, NormalizedPoint[]>,
  counting_lines: {} as Record<string, NormalizedPoint[]>,
  entrances: {} as Record<string, NormalizedPoint[]>,
  conflict_zones: {} as Record<string, NormalizedPoint[]>,
})
const sceneForm = ref({
  sceneId: 'scene-new',
  version: 1,
  name: 'New scene',
  cameraFingerprint: 'camera-new',
  width: 1920,
  height: 1080,
})
const calibrationJson = ref(JSON.stringify({
  calibration_id: 'calibration-v1',
  scene_id: '',
  scene_version: 1,
  mode: 'homography',
  image_reprojection_rmse_px: 0,
  world_checkpoint_rmse_m: 0,
  checkpoint_count: 4,
  matrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
}, null, 2))
const charucoFiles = ref<File[]>([])
const charucoForm = ref({
  squaresX: 7,
  squaresY: 5,
  squareLengthM: 0.04,
  markerLengthM: 0.02,
  dictionaryId: 0,
  minimumViews: 5,
  minimumCornersPerView: 4,
})
const charucoResult = ref<CharucoIntrinsics | null>(null)
const reviewForm = ref({
  operation: 'move_point',
  trackId: 0,
  frameIndex: 0,
  x: 0,
  y: 0,
  semanticClass: 'pedestrian',
  splitBeforeFrame: 0,
  newTrackId: 0,
  mergeTrackIds: '',
})
const pendingReviewOperations = ref<ReviewOperation[]>([])
let taskEvents: EventSource | null = null

const resultTabs = ['质量', '个体', '流量', '空间', 'OD', '交互']
const selectedTask = computed(() => tasks.value.find((item) => item.id === selectedTaskId.value))

const plotSpec = computed(() => {
  const analysis = results.value?.analysis as any
  if (!analysis) return { data: [], layout: { title: '等待正式分析结果' } }
  if (activeResultTab.value === '个体') {
    return {
      data: [{ type: 'bar', x: analysis.individual?.map((item: any) => String(item.track_id)), y: analysis.individual?.map((item: any) => item.mean_speed_mps), name: '平均速度' }],
      layout: { title: '个体平均速度', xaxis: { title: '轨迹 ID' }, yaxis: { title: 'm/s' } },
    }
  }
  if (activeResultTab.value === '流量') {
    return {
      data: [{ type: 'bar', x: analysis.flows?.map((item: any) => `${item.line_id}/${item.direction}`), y: analysis.flows?.map((item: any) => item.count) }],
      layout: { title: '断面分类与方向流量' },
    }
  }
  if (activeResultTab.value === '空间') {
    return {
      data: [{ type: 'scatter', mode: 'markers', x: analysis.spatial?.heatmap?.map((item: any) => item.x_index), y: analysis.spatial?.heatmap?.map((item: any) => item.y_index), marker: { color: analysis.spatial?.heatmap?.map((item: any) => item.kde_intensity), colorscale: 'Viridis', showscale: true } }],
      layout: { title: 'KDE 空间热力' },
    }
  }
  if (activeResultTab.value === 'OD') {
    return {
      data: [{ type: 'bar', x: analysis.od?.map((item: any) => `${item.origin}→${item.destination}`), y: analysis.od?.map((item: any) => item.count) }],
      layout: { title: '入口—出口矩阵' },
    }
  }
  if (activeResultTab.value === '交互') {
    return {
      data: [{ type: 'scatter', mode: 'markers', x: analysis.interactions?.map((item: any) => item.x), y: analysis.interactions?.map((item: any) => item.y), marker: { size: 12 }, text: analysis.interactions?.map((item: any) => `TTC ${item.ttc_seconds ?? '—'} s / PET ${item.pet_seconds ?? '—'} s`) }],
      layout: { title: '交互代理指标热点' },
    }
  }
  return {
    data: [{ type: 'bar', x: Object.keys(analysis.quality ?? {}), y: Object.values(analysis.quality ?? {}).map((value) => typeof value === 'number' ? value : 0) }],
    layout: { title: '轨迹与标定质量' },
  }
})

async function loadResources() {
  try {
    ;[models.value, scenes.value, tasks.value] = await Promise.all([
      visionApi.listModels(),
      visionApi.listScenes(),
      visionApi.listTasks(),
    ])
    modelId.value ||= models.value.find((item) => item.available)?.model_id ?? ''
    sceneId.value ||= scenes.value[0]?.scene_id ?? ''
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : String(reason)
  }
}

function onVideoChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0] ?? null
  videoFile.value = file
  if (videoPreview.value && typeof URL.revokeObjectURL === 'function') {
    URL.revokeObjectURL(videoPreview.value)
  }
  videoPreview.value = file && typeof URL.createObjectURL === 'function'
    ? URL.createObjectURL(file)
    : ''
}

async function createTask() {
  if (!videoFile.value || !taskName.value || !modelId.value) return
  submitting.value = true
  error.value = ''
  try {
    const created = await visionApi.createTask({
      taskName: taskName.value,
      modelId: modelId.value,
      sceneId: sceneId.value || undefined,
      video: videoFile.value,
    })
    tasks.value.unshift({
      id: created.task_id,
      task_name: taskName.value,
      status: created.status,
      model_id: modelId.value,
      scene_id: sceneId.value,
    })
    selectedTaskId.value = created.task_id
    connectTaskEvents(created.task_id)
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : String(reason)
  } finally {
    submitting.value = false
  }
}

async function selectTask(taskId: string) {
  selectedTaskId.value = taskId
  connectTaskEvents(taskId)
  await refreshSelectedTask(taskId)
}

function connectTaskEvents(taskId: string) {
  taskEvents?.close()
  taskEvents = visionApi.watchEvents(taskId, () => {
    void refreshSelectedTask(taskId)
  })
}

async function refreshSelectedTask(taskId: string) {
  try {
    const [nextTasks, nextResults] = await Promise.all([
      visionApi.listTasks(),
      visionApi.getResults(taskId),
    ])
    tasks.value = nextTasks
    if (selectedTaskId.value === taskId) {
      results.value = nextResults
      if (['completed', 'failed', 'cancelled'].includes(nextResults.task.status)) {
        taskEvents?.close()
        taskEvents = null
      }
    }
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : String(reason)
  }
}

function addGeometryPoint(event: MouseEvent) {
  const target = event.currentTarget as SVGElement
  const bounds = target.getBoundingClientRect()
  geometryPoints.value.push({
    x: Math.round(((event.clientX - bounds.left) / bounds.width) * 1000) / 1000,
    y: Math.round(((event.clientY - bounds.top) / bounds.height) * 1000) / 1000,
  })
}

function syncVideoResolution(event: Event) {
  const video = event.currentTarget as HTMLVideoElement
  if (video.videoWidth > 0 && video.videoHeight > 0) {
    sceneForm.value.width = video.videoWidth
    sceneForm.value.height = video.videoHeight
  }
}

function stageGeometry() {
  const points = geometryPoints.value.map((point) => ({ ...point }))
  const isLine = geometryMode.value === 'counting_lines'
  if ((isLine && points.length !== 2) || (!isLine && points.length < 3)) {
    error.value = isLine ? '计数线必须正好包含两个点' : '多边形至少需要三个点'
    return
  }
  if (geometryMode.value === 'roi') {
    storedGeometry.value.roi = points
  } else {
    const name = geometryName.value.trim()
    if (!name) {
      error.value = '请填写图形名称'
      return
    }
    const collection = storedGeometry.value[
      geometryMode.value as keyof Omit<typeof storedGeometry.value, 'roi'>
    ] as Record<string, NormalizedPoint[]>
    collection[name] = points
  }
  geometryPoints.value = []
  error.value = ''
}

function toPixelPoints(points: NormalizedPoint[]): PixelPoint[] {
  return points.map((point) => [
    Math.round(point.x * sceneForm.value.width * 1000) / 1000,
    Math.round(point.y * sceneForm.value.height * 1000) / 1000,
  ])
}

function toPixelCollection(collection: Record<string, NormalizedPoint[]>) {
  return Object.fromEntries(
    Object.entries(collection).map(([name, points]) => [name, toPixelPoints(points)]),
  )
}

async function saveSceneProfile() {
  if (storedGeometry.value.roi.length < 3) {
    error.value = '请先暂存 ROI'
    return
  }
  try {
    const calibrationReport = {
      ...JSON.parse(calibrationJson.value),
      scene_id: sceneForm.value.sceneId,
      scene_version: sceneForm.value.version,
    }
    const saved = await visionApi.createSceneFromPixelGeometry({
      scene_id: sceneForm.value.sceneId,
      version: sceneForm.value.version,
      name: sceneForm.value.name,
      camera_fingerprint: sceneForm.value.cameraFingerprint,
      resolution: [sceneForm.value.width, sceneForm.value.height],
      calibration_report: calibrationReport,
      roi: toPixelPoints(storedGeometry.value.roi),
      exclusion_zones: toPixelCollection(storedGeometry.value.exclusion_zones),
      zones: toPixelCollection(storedGeometry.value.zones),
      counting_lines: toPixelCollection(storedGeometry.value.counting_lines),
      entrances: toPixelCollection(storedGeometry.value.entrances),
      conflict_zones: toPixelCollection(storedGeometry.value.conflict_zones),
    })
    scenes.value = await visionApi.listScenes()
    sceneId.value = saved.scene_id
    error.value = ''
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : String(reason)
  }
}

function onCharucoImages(event: Event) {
  charucoFiles.value = Array.from((event.target as HTMLInputElement).files ?? [])
}

async function submitCharuco() {
  if (!charucoFiles.value.length) return
  try {
    charucoResult.value = await visionApi.calibrateCharuco({
      images: charucoFiles.value,
      ...charucoForm.value,
    })
    const current = JSON.parse(calibrationJson.value)
    calibrationJson.value = JSON.stringify({
      ...current,
      mode: 'full_camera',
      image_reprojection_rmse_px: charucoResult.value.rms_reprojection_error_px,
      camera_matrix: charucoResult.value.camera_matrix,
      distortion: charucoResult.value.distortion,
    }, null, 2)
    error.value = ''
  } catch (reason) {
    error.value = reason instanceof Error ? reason.message : String(reason)
  }
}

async function submitCalibration() {
  if (!selectedTaskId.value) return
  const report = JSON.parse(calibrationJson.value)
  await visionApi.submitCalibration(selectedTaskId.value, report)
  await selectTask(selectedTaskId.value)
}

function buildReviewOperation(): ReviewOperation {
  if (reviewForm.value.operation === 'delete_track') {
    return { operation: 'delete_track', track_id: reviewForm.value.trackId }
  }
  if (reviewForm.value.operation === 'relabel_track') {
    return {
      operation: 'relabel_track',
      track_id: reviewForm.value.trackId,
      semantic_class: reviewForm.value.semanticClass,
    }
  }
  if (reviewForm.value.operation === 'split_track') {
    return {
      operation: 'split_track',
      track_id: reviewForm.value.trackId,
      split_before_frame: reviewForm.value.splitBeforeFrame,
      new_track_id: reviewForm.value.newTrackId,
    }
  }
  if (reviewForm.value.operation === 'merge_tracks') {
    return {
      operation: 'merge_tracks',
      track_ids: reviewForm.value.mergeTrackIds
        .split(',')
        .map((item) => Number(item.trim()))
        .filter(Number.isInteger),
      new_track_id: reviewForm.value.newTrackId,
    }
  }
  return {
    operation: 'move_point',
    track_id: reviewForm.value.trackId,
    frame_index: reviewForm.value.frameIndex,
    point: { x: reviewForm.value.x, y: reviewForm.value.y },
  }
}

function addReviewOperation() {
  pendingReviewOperations.value.push(buildReviewOperation())
}

async function submitReview() {
  if (!selectedTaskId.value) return
  const parent = results.value?.artifacts.find((item) => item.artifact_type === 'pixel_tracks')
  if (!parent) return
  if (!pendingReviewOperations.value.length) addReviewOperation()
  await visionApi.submitReview(selectedTaskId.value, {
    patch_id: `patch-${Date.now()}`,
    parent_artifact_id: parent.artifact_id,
    operations: pendingReviewOperations.value,
  })
  pendingReviewOperations.value = []
  await selectTask(selectedTaskId.value)
}

onMounted(loadResources)
onBeforeUnmount(() => {
  taskEvents?.close()
  taskEvents = null
  if (videoPreview.value && typeof URL.revokeObjectURL === 'function') {
    URL.revokeObjectURL(videoPreview.value)
  }
})
</script>

<template>
  <section class="vision-page">
    <header class="vision-heading">
      <div>
        <p class="eyebrow">Vision trajectory laboratory</p>
        <h2>视觉轨迹分析</h2>
        <p>从混流视频、人工复核与相机标定，生成可追溯的米制轨迹和多层分析图。</p>
      </div>
      <div class="vision-gate" :data-ready="results?.physical_metrics_available">
        <strong>{{ results?.physical_metrics_available ? '米制指标可用' : '等待 10 cm 标定门槛' }}</strong>
        <span>不输出标注结果视频</span>
      </div>
    </header>

    <p v-if="error" class="page-error">{{ error }}</p>

    <div class="vision-layout">
      <aside class="vision-rail">
        <form data-area="task-create" class="vision-card task-create" @submit.prevent="createTask">
          <p class="section-label">01 / Create</p>
          <h3>新建视频任务</h3>
          <label>任务名称<input v-model="taskName" name="task_name" required /></label>
          <label>模型<select v-model="modelId" name="model_id" required><option value="">选择模型</option><option v-for="model in models" :key="model.model_id" :value="model.model_id" :disabled="!model.available">{{ model.name }} · {{ model.input_size || 'manifest' }}</option></select></label>
          <label>场景<select v-model="sceneId" name="scene_id"><option value="">稍后标定</option><option v-for="scene in scenes" :key="scene.scene_id" :value="scene.scene_id">{{ scene.name }} · v{{ scene.version }}</option></select></label>
          <label>源视频<input type="file" accept="video/*" required @change="onVideoChange" /></label>
          <button :disabled="submitting || !videoFile">{{ submitting ? '上传中…' : '上传并排队' }}</button>
        </form>

        <section class="vision-card task-list">
          <p class="section-label">02 / Queue</p>
          <h3>单 GPU 队列</h3>
          <button v-for="task in tasks" :key="task.id" class="task-row" :class="{ active: task.id === selectedTaskId }" @click="selectTask(task.id)">
            <span><strong>{{ task.task_name }}</strong><small>{{ task.id }}</small></span>
            <em :data-status="task.status">{{ task.status }}</em>
          </button>
          <p v-if="!tasks.length" class="empty-copy">还没有视觉任务。</p>
        </section>
      </aside>

      <main class="vision-workspace">
        <section class="vision-card scene-stage" data-area="calibration-wizard">
          <div class="section-heading"><p class="section-label">03 / Calibrate</p><h3>场景与标定向导</h3></div>
          <div class="scene-grid">
            <div class="video-stage">
              <video v-if="videoPreview" :src="videoPreview" controls muted @loadedmetadata="syncVideoResolution"></video>
              <div v-else class="video-placeholder">上传视频后在首帧上绘制 ROI、分区、计数线和冲突区。</div>
              <svg viewBox="0 0 1 1" preserveAspectRatio="none" @click="addGeometryPoint">
                <polyline :points="geometryPoints.map((point) => `${point.x},${point.y}`).join(' ')" />
                <circle v-for="(point, index) in geometryPoints" :key="index" :cx="point.x" :cy="point.y" r="0.008" />
              </svg>
            </div>
            <div class="calibration-controls">
              <div class="review-form">
                <label>场景 ID<input v-model="sceneForm.sceneId" name="scene_profile_id" /></label>
                <label>版本<input v-model.number="sceneForm.version" type="number" min="1" /></label>
                <label>场景名称<input v-model="sceneForm.name" name="scene_profile_name" /></label>
                <label>相机指纹<input v-model="sceneForm.cameraFingerprint" name="camera_fingerprint" /></label>
                <label>宽度<input v-model.number="sceneForm.width" name="scene_width" type="number" min="1" /></label>
                <label>高度<input v-model.number="sceneForm.height" name="scene_height" type="number" min="1" /></label>
              </div>
              <label>绘制对象<select v-model="geometryMode"><option value="roi">ROI</option><option value="zones">分区</option><option value="counting_lines">计数线</option><option value="entrances">出入口</option><option value="conflict_zones">冲突区</option><option value="exclusion_zones">排除区</option></select></label>
              <label v-if="geometryMode !== 'roi'">图形名称<input v-model="geometryName" /></label>
              <button data-action="stage-geometry" class="secondary-action" @click="stageGeometry">暂存当前图形</button>
              <button class="secondary-action" @click="geometryPoints = []">清空当前图形</button>
              <p>当前 {{ geometryPoints.length }} 点；已暂存 ROI {{ storedGeometry.roi.length }} 点。保存时由标定报告投影为世界坐标。</p>
              <button data-action="save-scene" @click="saveSceneProfile">保存 SceneProfile 新版本</button>
              <details>
                <summary>ChArUco 内参向导</summary>
                <label>标定图片<input name="charuco_images" type="file" accept="image/*" multiple @change="onCharucoImages" /></label>
                <div class="review-form">
                  <label>横向方格<input v-model.number="charucoForm.squaresX" type="number" min="2" /></label>
                  <label>纵向方格<input v-model.number="charucoForm.squaresY" type="number" min="2" /></label>
                  <label>方格边长 (m)<input v-model.number="charucoForm.squareLengthM" type="number" step="0.001" /></label>
                  <label>标记边长 (m)<input v-model.number="charucoForm.markerLengthM" type="number" step="0.001" /></label>
                  <label>字典 ID<input v-model.number="charucoForm.dictionaryId" type="number" min="0" /></label>
                  <label>最少视角<input v-model.number="charucoForm.minimumViews" type="number" min="3" /></label>
                </div>
                <button data-action="calibrate-charuco" :disabled="!charucoFiles.length" @click="submitCharuco">计算相机内参</button>
                <p v-if="charucoResult" data-area="charuco-result">{{ charucoResult.valid_view_count }} 个有效视角，重投影 RMS {{ charucoResult.rms_reprojection_error_px }} px</p>
              </details>
              <label>CalibrationReport JSON<textarea v-model="calibrationJson" rows="10"></textarea></label>
              <button :disabled="!selectedTask" @click="submitCalibration">提交标定报告</button>
            </div>
          </div>
        </section>

        <section class="vision-card review-stage" data-area="review-editor">
          <div class="section-heading"><p class="section-label">04 / Review</p><h3>异常轨迹复核</h3></div>
          <div class="review-summary">
            <span>降级点 {{ results?.review_queue?.length ?? 0 }}</span>
            <span>任务状态 {{ selectedTask?.status ?? '未选择' }}</span>
            <span>支持删轨、改类、拆分、合并和落地点修正</span>
          </div>
          <form class="review-form" @submit.prevent="submitReview">
            <label>操作<select v-model="reviewForm.operation" name="review_operation"><option value="move_point">落地点修正</option><option value="delete_track">删除轨迹</option><option value="relabel_track">修改类别</option><option value="split_track">拆分轨迹</option><option value="merge_tracks">合并轨迹</option></select></label>
            <label v-if="reviewForm.operation !== 'merge_tracks'">轨迹 ID<input v-model.number="reviewForm.trackId" name="review_track_id" type="number" min="0" /></label>
            <template v-if="reviewForm.operation === 'move_point'">
              <label>帧号<input v-model.number="reviewForm.frameIndex" type="number" min="0" /></label>
              <label>像素 X<input v-model.number="reviewForm.x" type="number" step="0.1" /></label>
              <label>像素 Y<input v-model.number="reviewForm.y" type="number" step="0.1" /></label>
            </template>
            <label v-if="reviewForm.operation === 'relabel_track'">类别<select v-model="reviewForm.semanticClass" name="review_semantic_class"><option value="pedestrian">普通行人</option><option value="pedestrian_umbrella">撑伞行人</option><option value="bicycle_rider">自行车骑行者</option><option value="ebike_rider">电瓶车骑行者</option></select></label>
            <label v-if="reviewForm.operation === 'split_track'">拆分前帧<input v-model.number="reviewForm.splitBeforeFrame" type="number" min="0" /></label>
            <label v-if="reviewForm.operation === 'merge_tracks'">轨迹 ID 列表<input v-model="reviewForm.mergeTrackIds" placeholder="1,2" /></label>
            <label v-if="['split_track', 'merge_tracks'].includes(reviewForm.operation)">新轨迹 ID<input v-model.number="reviewForm.newTrackId" type="number" min="0" /></label>
            <button data-action="add-review-operation" type="button" class="secondary-action" :disabled="selectedTask?.status !== 'awaiting_review'" @click="addReviewOperation">加入补丁</button>
            <button data-action="submit-review" :disabled="selectedTask?.status !== 'awaiting_review'">提交 {{ pendingReviewOperations.length || 1 }} 项复核</button>
          </form>
        </section>

        <section class="vision-card result-stage">
          <div class="result-header"><div><p class="section-label">05 / Analyze</p><h3>多层结果</h3></div><div class="result-tabs"><button v-for="tab in resultTabs" :key="tab" data-result-tab :class="{ active: activeResultTab === tab }" @click="activeResultTab = tab">{{ tab }}</button></div></div>
          <PlotlyPanel :data="plotSpec.data" :layout="plotSpec.layout" />
          <pre class="result-json">{{ results?.analysis?.[activeResultTab === '质量' ? 'quality' : activeResultTab === '个体' ? 'individual' : activeResultTab === '流量' ? 'flows' : activeResultTab === '空间' ? 'spatial' : activeResultTab === 'OD' ? 'od' : 'interactions'] ?? '等待结果' }}</pre>
        </section>
      </main>
    </div>
  </section>
</template>
