import { describe, expect, it } from 'vitest'

import { initialRunState, reduceRunEvent } from '../src/services/agentStream'


describe('verified answer stream', () => {
  it('keeps answer deltas hidden until run.completed', () => {
    const withStage = reduceRunEvent(initialRunState(), 'stage.started', {
      stage: 'semantic_verify',
    })
    const withDelta = reduceRunEvent(withStage, 'answer.delta', {
      delta: 'Verified answer [L1]',
      verified: true,
    })

    expect(withDelta.visibleAnswer).toBe('')
    expect(withDelta.stage).toBe('semantic_verify')

    const completed = reduceRunEvent(withDelta, 'run.completed', {})
    expect(completed.visibleAnswer).toBe('Verified answer [L1]')
    expect(completed.status).toBe('completed')
  })

  it('clears pending answer text when a run fails', () => {
    const withDelta = reduceRunEvent(initialRunState(), 'answer.delta', {
      delta: 'draft',
      verified: true,
    })
    const failed = reduceRunEvent(withDelta, 'run.failed', { error: 'run execution failed' })

    expect(failed.visibleAnswer).toBe('')
    expect(failed.pendingAnswer).toBe('')
    expect(failed.status).toBe('failed')
  })
})
