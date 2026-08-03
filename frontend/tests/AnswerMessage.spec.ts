import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AnswerMessage from '../src/components/AnswerMessage.vue'
import type { EvidenceItem, MessageCitation } from '../src/services/agentApi'


describe('AnswerMessage', () => {
  it('renders source badges, evidence details, limitations and inferences separately', () => {
    const wrapper = mount(AnswerMessage, {
      props: {
        message: {
          id: 'message-1',
          role: 'assistant',
          content: 'Answer [L1] [A1] [W1]',
          answer_document: {
            answer_markdown: 'Answer [L1] [A1] [W1]',
            citations: [],
            limitations: ['Only one local regulation was available.'],
            inferences: [{ text: 'Conduct an on-site review.', basis_evidence_ids: ['local-1'] }],
            verification: {
              status: 'verified',
              rules_passed: true,
              semantic_passed: true,
            },
          },
          citations: [
            citation('L1', 'local_official', 'page 4'),
            citation('A1', 'external_academic', 'abstract'),
            citation('W1', 'external_web', 'web page'),
          ],
        },
      },
    })

    expect(wrapper.find('[data-origin="local_official"]').text()).toContain('本地正式证据')
    expect(wrapper.find('[data-origin="external_academic"]').text()).toContain('外部学术')
    expect(wrapper.find('[data-origin="external_web"]').text()).toContain('外部网页')
    expect(wrapper.text()).toContain('page 4')
    expect(wrapper.find('[data-area="limitations"]').text()).toContain('Only one local')
    expect(wrapper.find('[data-area="inferences"]').text()).toContain('Conduct an on-site')
  })

  it('shows a prominent warning for rules-only answers', () => {
    const wrapper = mount(AnswerMessage, {
      props: {
        message: {
          id: 'message-2',
          role: 'assistant',
          content: 'Rules-only answer',
          answer_document: {
            answer_markdown: 'Rules-only answer',
            citations: [],
            limitations: [],
            inferences: [],
            verification: {
              status: 'rules_only',
              rules_passed: true,
              semantic_passed: null,
            },
          },
          citations: [],
        },
      },
    })

    expect(wrapper.get('[role="alert"]').text()).toContain('仅完成引用规则校验')
  })

  it('shows an informational banner without citations when evidence is insufficient', () => {
    const wrapper = mount(AnswerMessage, {
      props: {
        message: {
          id: 'message-3',
          role: 'assistant',
          content: '当前知识库与外部检索未找到足够的可核验证据，暂时无法给出可靠回答。',
          answer_document: {
            answer_markdown:
              '当前知识库与外部检索未找到足够的可核验证据，暂时无法给出可靠回答。',
            citations: [],
            limitations: ['当前知识库与外部检索未找到足够的可核验证据。'],
            inferences: [],
            verification: {
              status: 'insufficient_evidence',
              rules_passed: true,
              semantic_passed: null,
            },
          },
          citations: [],
        },
      },
    })

    expect(wrapper.get('[data-verification="insufficient_evidence"]').text()).toContain(
      '未找到足够的可核验证据',
    )
    expect(wrapper.findAll('.citation-card')).toHaveLength(0)
  })
})


function citation(label: string, origin: EvidenceItem['origin'], locator: string): MessageCitation {
  return {
    label,
    claim_ids: ['c1'],
    evidence: {
      evidence_id: `${origin}-1`,
      origin,
      title: `${origin} source`,
      quote: 'Quoted evidence.',
      locator,
      retrieved_at: '2026-07-30T00:00:00Z',
      content_hash: 'a'.repeat(64),
      score: 0.9,
    },
  }
}
