<script setup lang="ts">
import type { ConversationMessage, EvidenceItem } from '../services/agentApi'

defineProps<{ message: ConversationMessage }>()

const originLabel: Record<EvidenceItem['origin'], string> = {
  local_official: '本地正式证据',
  external_academic: '外部学术',
  external_web: '外部网页',
}

function accessTime(value: string): string {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value))
}
</script>

<template>
  <article class="answer-message">
    <div
      v-if="message.answer_document?.verification.status === 'rules_only'"
      class="verification-warning"
      role="alert"
    >
      仅完成引用规则校验，语义复核已在本机配置中显式关闭。
    </div>

    <div
      v-if="message.answer_document?.verification.status === 'insufficient_evidence'"
      class="verification-warning"
      data-verification="insufficient_evidence"
    >
      未找到足够的可核验证据，本次未生成事实性回答。
    </div>

    <div class="answer-copy">{{ message.content }}</div>

    <section v-if="message.citations.length" class="citation-stack" aria-label="回答引用">
      <details v-for="citation in message.citations" :key="citation.label" class="citation-card">
        <summary>
          <span class="citation-label">[{{ citation.label }}]</span>
          <span class="origin-badge" :data-origin="citation.evidence.origin">
            {{ originLabel[citation.evidence.origin] }}
          </span>
          <strong>{{ citation.evidence.title }}</strong>
        </summary>
        <blockquote>{{ citation.evidence.quote }}</blockquote>
        <dl>
          <div v-if="citation.evidence.locator">
            <dt>定位</dt>
            <dd>{{ citation.evidence.locator }}</dd>
          </div>
          <div>
            <dt>访问时间</dt>
            <dd>{{ accessTime(citation.evidence.retrieved_at) }}</dd>
          </div>
          <div v-if="citation.evidence.doi">
            <dt>DOI</dt>
            <dd>{{ citation.evidence.doi }}</dd>
          </div>
        </dl>
        <a
          v-if="citation.evidence.url"
          :href="citation.evidence.url"
          target="_blank"
          rel="noreferrer"
        >
          打开来源
        </a>
      </details>
    </section>

    <section
      v-if="message.answer_document?.limitations.length"
      class="answer-aside"
      data-area="limitations"
    >
      <h4>局限</h4>
      <ul>
        <li v-for="item in message.answer_document.limitations" :key="item">{{ item }}</li>
      </ul>
    </section>

    <section
      v-if="message.answer_document?.inferences.length"
      class="answer-aside inference-aside"
      data-area="inferences"
    >
      <h4>[I] 分析性推断</h4>
      <ul>
        <li v-for="item in message.answer_document.inferences" :key="item.text">
          {{ item.text }}
        </li>
      </ul>
    </section>
  </article>
</template>
