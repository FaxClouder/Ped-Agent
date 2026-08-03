export interface EvidenceItem {
  evidence_id: string
  origin: 'local_official' | 'external_academic' | 'external_web'
  title: string
  quote: string
  locator?: string | null
  url?: string | null
  doi?: string | null
  retrieved_at: string
  content_hash: string
  score: number
}

export interface MessageCitation {
  label: string
  claim_ids: string[]
  evidence: EvidenceItem
}

export interface AnswerDocument {
  answer_markdown: string
  citations: Array<{ label: string; evidence_id: string; claim_ids: string[] }>
  inferences: Array<{ text: string; basis_evidence_ids: string[] }>
  limitations: string[]
  verification: {
    status: 'verified' | 'rules_only' | 'insufficient_evidence'
    rules_passed: boolean
    semantic_passed: boolean | null
    repaired?: boolean
  }
}

export interface ConversationMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  answer_document: AnswerDocument | null
  citations: MessageCitation[]
  created_at?: string
}

export interface RunRecord {
  id: string
  status: string
  query: string
}

export interface ConversationSummary {
  id: string
  title: string | null
  latest_run_status?: string | null
  updated_at: string
}

export interface ConversationDetail extends ConversationSummary {
  messages: ConversationMessage[]
  runs: RunRecord[]
}

async function requestJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string }
    throw new Error(body.detail ?? `请求失败 (${response.status})`)
  }
  return (await response.json()) as T
}

export const agentApi = {
  listConversations: () => requestJson<ConversationSummary[]>('/api/conversations'),
  createConversation: (title?: string) =>
    requestJson<ConversationSummary>('/api/conversations', {
      method: 'POST',
      body: JSON.stringify({ title: title || null }),
    }),
  getConversation: (id: string) => requestJson<ConversationDetail>(`/api/conversations/${id}`),
  createRun: (conversationId: string, query: string) =>
    requestJson<{ run_id: string; events_url: string }>(
      `/api/conversations/${conversationId}/runs`,
      { method: 'POST', body: JSON.stringify({ query }) },
    ),
  cancelRun: (runId: string) =>
    requestJson<{ run_id: string; status: string }>(`/api/runs/${runId}/cancel`, {
      method: 'POST',
    }),
}
