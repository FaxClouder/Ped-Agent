export type RunEventName =
  | 'run.started'
  | 'stage.started'
  | 'stage.completed'
  | 'evidence.summary'
  | 'answer.delta'
  | 'run.completed'
  | 'run.failed'
  | 'run.cancelled'
  | 'heartbeat'

export type RunUiStatus =
  | 'idle'
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'reconnecting'

export interface RunUiState {
  status: RunUiStatus
  stage: string
  pendingAnswer: string
  visibleAnswer: string
  evidenceSummary: Record<string, unknown> | null
  error: string
  lastEventId: string
}

export function initialRunState(status: RunUiStatus = 'idle'): RunUiState {
  return {
    status,
    stage: '',
    pendingAnswer: '',
    visibleAnswer: '',
    evidenceSummary: null,
    error: '',
    lastEventId: '',
  }
}

export function reduceRunEvent(
  state: RunUiState,
  event: RunEventName,
  payload: Record<string, unknown>,
  lastEventId = state.lastEventId,
): RunUiState {
  const next = { ...state, lastEventId }
  if (event === 'run.started') return { ...next, status: 'running' }
  if (event === 'stage.started') return { ...next, status: 'running', stage: String(payload.stage ?? '') }
  if (event === 'evidence.summary') return { ...next, evidenceSummary: payload }
  if (event === 'answer.delta') {
    return { ...next, pendingAnswer: next.pendingAnswer + String(payload.delta ?? '') }
  }
  if (event === 'run.completed') {
    return {
      ...next,
      status: 'completed',
      stage: '',
      visibleAnswer: next.pendingAnswer,
    }
  }
  if (event === 'run.failed') {
    return {
      ...next,
      status: 'failed',
      stage: '',
      pendingAnswer: '',
      visibleAnswer: '',
      error: String(payload.error ?? '运行失败'),
    }
  }
  if (event === 'run.cancelled') {
    return {
      ...next,
      status: 'cancelled',
      stage: '',
      pendingAnswer: '',
      visibleAnswer: '',
    }
  }
  return next
}

const eventNames: RunEventName[] = [
  'run.started',
  'stage.started',
  'stage.completed',
  'evidence.summary',
  'answer.delta',
  'run.completed',
  'run.failed',
  'run.cancelled',
  'heartbeat',
]

export function subscribeToRun(
  eventsUrl: string,
  onEvent: (event: RunEventName, payload: Record<string, unknown>, lastEventId: string) => void,
  onReconnect: () => void,
): () => void {
  const source = new EventSource(eventsUrl)
  for (const eventName of eventNames) {
    source.addEventListener(eventName, (event) => {
      const message = event as MessageEvent<string>
      const payload = message.data ? (JSON.parse(message.data) as Record<string, unknown>) : {}
      onEvent(eventName, payload, message.lastEventId)
      if (['run.completed', 'run.failed', 'run.cancelled'].includes(eventName)) source.close()
    })
  }
  source.onerror = () => {
    if (source.readyState !== EventSource.CLOSED) onReconnect()
  }
  return () => source.close()
}
