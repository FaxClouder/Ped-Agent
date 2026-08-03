<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import AnswerMessage from '../components/AnswerMessage.vue'
import {
  agentApi,
  type ConversationDetail,
  type ConversationSummary,
} from '../services/agentApi'
import {
  initialRunState,
  reduceRunEvent,
  subscribeToRun,
  type RunEventName,
} from '../services/agentStream'

const conversations = ref<ConversationSummary[]>([])
const activeConversation = ref<ConversationDetail | null>(null)
const query = ref('')
const loading = ref(true)
const submitting = ref(false)
const pageError = ref('')
const runId = ref('')
const runState = ref(initialRunState())
let closeStream: (() => void) | null = null

const isRunActive = computed(() => ['queued', 'running', 'reconnecting'].includes(runState.value.status))
const stageLabel = computed(() => {
  const labels: Record<string, string> = {
    load_conversation: '加载会话上下文',
    preflight_local_retrieval: '预检索本地正式证据',
    assess_evidence: '判断证据充分性',
    external_search: '补充外部证据',
    normalize_evidence: '归一化 Evidence Pack',
    handle_insufficient_evidence: '生成证据不足结果',
    rewrite_query: '改写独立检索问题',
    refined_local_retrieval: '按独立问题精检本地证据',
    merge_refined_evidence: '合并并归一化 Evidence Pack',
    generate_draft: '生成结构化草稿',
    validate_rules: '校验 Claim 与引用',
    semantic_verify: '执行语义复核',
    revise_once: '收紧或删除未支持表述',
    final_persist: '持久化已验证答案',
  }
  return labels[runState.value.stage] ?? '准备运行'
})

onMounted(async () => {
  await refreshConversations()
  if (conversations.value[0]) await selectConversation(conversations.value[0].id)
  loading.value = false
})

onBeforeUnmount(() => closeStream?.())

async function refreshConversations(): Promise<void> {
  try {
    conversations.value = await agentApi.listConversations()
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : '会话加载失败'
  }
}

async function newConversation(): Promise<void> {
  pageError.value = ''
  const created = await agentApi.createConversation('新证据问答')
  await refreshConversations()
  await selectConversation(created.id)
}

async function selectConversation(id: string): Promise<void> {
  closeStream?.()
  closeStream = null
  activeConversation.value = await agentApi.getConversation(id)
  const activeRun = [...activeConversation.value.runs]
    .reverse()
    .find((run) => ['queued', 'running'].includes(run.status))
  if (activeRun) {
    runId.value = activeRun.id
    runState.value = initialRunState(activeRun.status === 'queued' ? 'queued' : 'running')
    connect(`/api/runs/${activeRun.id}/events`)
  } else {
    runId.value = ''
    runState.value = initialRunState()
  }
}

async function submit(): Promise<void> {
  const normalized = query.value.trim()
  if (!normalized || submitting.value || isRunActive.value) return
  submitting.value = true
  pageError.value = ''
  try {
    if (!activeConversation.value) await newConversation()
    if (!activeConversation.value) throw new Error('无法创建会话')
    const result = await agentApi.createRun(activeConversation.value.id, normalized)
    query.value = ''
    runId.value = result.run_id
    runState.value = initialRunState('queued')
    activeConversation.value = await agentApi.getConversation(activeConversation.value.id)
    connect(result.events_url)
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : '提交失败'
  } finally {
    submitting.value = false
  }
}

function connect(eventsUrl: string): void {
  closeStream?.()
  closeStream = subscribeToRun(eventsUrl, handleEvent, () => {
    runState.value = { ...runState.value, status: 'reconnecting' }
  })
}

async function handleEvent(
  event: RunEventName,
  payload: Record<string, unknown>,
  lastEventId: string,
): Promise<void> {
  runState.value = reduceRunEvent(runState.value, event, payload, lastEventId)
  if (['run.completed', 'run.failed', 'run.cancelled'].includes(event)) {
    closeStream?.()
    closeStream = null
    if (activeConversation.value) {
      activeConversation.value = await agentApi.getConversation(activeConversation.value.id)
      await refreshConversations()
    }
  }
}

async function cancel(): Promise<void> {
  if (!runId.value) return
  try {
    await agentApi.cancelRun(runId.value)
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : '取消失败'
  }
}
</script>

<template>
  <section class="answer-page">
    <header class="answer-heading">
      <div>
        <p class="eyebrow">Evidence QA / Verified output only</p>
        <h2>智能问答</h2>
        <p>回答在引用规则与语义复核完成前保持隐藏；外部证据不会自动进入正式知识库。</p>
      </div>
      <button type="button" class="secondary-action" @click="newConversation">新建会话</button>
    </header>

    <p v-if="pageError" class="page-error" role="alert">{{ pageError }}</p>

    <div class="answer-workspace" :aria-busy="loading">
      <aside class="conversation-rail" aria-label="会话列表">
        <p class="section-label">Conversations</p>
        <button
          v-for="item in conversations"
          :key="item.id"
          type="button"
          :class="['conversation-item', { active: activeConversation?.id === item.id }]"
          @click="selectConversation(item.id)"
        >
          <strong>{{ item.title || '未命名会话' }}</strong>
          <small>{{ item.latest_run_status || 'ready' }}</small>
        </button>
        <p v-if="!loading && !conversations.length" class="empty-copy">尚无会话。</p>
      </aside>

      <main class="conversation-panel">
        <div class="message-list" aria-live="polite">
          <template v-if="activeConversation?.messages.length">
            <article
              v-for="message in activeConversation.messages"
              :key="message.id"
              :class="['message-row', `message-${message.role}`]"
            >
              <p v-if="message.role === 'user'">{{ message.content }}</p>
              <AnswerMessage v-else-if="message.role === 'assistant'" :message="message" />
            </article>
          </template>
          <div v-else class="answer-empty">
            <span>Evidence-bound</span>
            <h3>从一个需要证据支持的问题开始</h3>
            <p>可询问行人流机理、实验测量、设施规范或安全干预。</p>
          </div>

          <section v-if="isRunActive" class="run-progress" aria-label="回答验证进度">
            <div class="progress-pulse" aria-hidden="true"></div>
            <div>
              <strong>{{ stageLabel }}</strong>
              <p>草稿不会在验证完成前显示。</p>
            </div>
            <button type="button" class="cancel-action" @click="cancel">取消</button>
          </section>
        </div>

        <form class="answer-composer" @submit.prevent="submit">
          <label for="agent-query">问题</label>
          <textarea
            id="agent-query"
            v-model="query"
            rows="3"
            :disabled="isRunActive"
            placeholder="例如：瓶颈附近密度升高时，规范与实验文献分别支持哪些判断？"
          ></textarea>
          <div>
            <span>只展示已验证回答</span>
            <button type="submit" :disabled="!query.trim() || isRunActive || submitting">
              {{ submitting ? '提交中' : '提交问题' }}
            </button>
          </div>
        </form>
      </main>

      <aside class="answer-inspector" aria-label="证据链说明">
        <p class="section-label">Evidence protocol</p>
        <h3>回答链</h3>
        <ol>
          <li><span>01</span>本地 FTS5 + Chroma</li>
          <li><span>02</span>必要时单轮外搜</li>
          <li><span>03</span>Claim 引用校验</li>
          <li><span>04</span>语义支持度复核</li>
          <li><span>05</span>最多一次修订</li>
        </ol>
        <dl v-if="runState.evidenceSummary" class="evidence-counts">
          <div><dt>Local</dt><dd>{{ runState.evidenceSummary.local ?? 0 }}</dd></div>
          <div><dt>Academic</dt><dd>{{ runState.evidenceSummary.academic ?? 0 }}</dd></div>
          <div><dt>Web</dt><dd>{{ runState.evidenceSummary.web ?? 0 }}</dd></div>
        </dl>
      </aside>
    </div>
  </section>
</template>
