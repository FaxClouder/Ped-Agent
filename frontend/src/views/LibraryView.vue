<template>
  <section class="library-page">
    <header class="page-heading">
      <div>
        <p class="eyebrow">Knowledge foundation / Phase 1</p>
        <h2>知识库</h2>
        <p class="page-intro">
          浏览已核验文献、法规与标准，并定位到可复查的原文页码或条款。
        </p>
      </div>
      <div class="readiness" aria-label="当前知识库状态">
        <span class="readiness-dot" aria-hidden="true"></span>
        <span>等待试点资料导入</span>
      </div>
    </header>

    <div class="workspace-grid">
      <div class="workspace-primary">
        <section class="control-panel" data-area="filters" aria-labelledby="filter-title">
          <div class="section-heading">
            <p class="section-label">01 / Scope</p>
            <h3 id="filter-title">收窄证据范围</h3>
          </div>
          <div class="filter-grid">
            <label>
              <span>资料类型</span>
              <select disabled>
                <option>全部类型</option>
              </select>
            </label>
            <label>
              <span>主题</span>
              <input disabled placeholder="例如：瓶颈、基本图" />
            </label>
            <label>
              <span>年份</span>
              <input disabled placeholder="YYYY" />
            </label>
            <label>
              <span>效力状态</span>
              <select disabled>
                <option>全部状态</option>
              </select>
            </label>
          </div>
        </section>

        <section class="search-panel" data-area="search" aria-labelledby="search-title">
          <div class="section-heading">
            <p class="section-label">02 / Retrieve</p>
            <h3 id="search-title">检索原文证据</h3>
          </div>
          <form class="search-form">
            <label class="search-field">
              <span class="sr-only">检索问题</span>
              <input disabled placeholder="搜索文献、法规、主题、数据集或条款" />
            </label>
            <button type="button" disabled>检索</button>
          </form>
        </section>

        <section class="library-placeholder" aria-label="资料列表占位区">
          <p class="section-label">Library index</p>
          <div class="placeholder-rule"></div>
          <p>资料导入后，这里将显示标题、类型、年份、主题和有效状态。</p>
        </section>
      </div>

      <aside class="evidence-panel" data-area="evidence" aria-labelledby="evidence-title">
        <p class="section-label">03 / Inspect</p>
        <h3 id="evidence-title">证据详情</h3>
        <div class="folio-mark" aria-hidden="true">P.</div>
        <p class="evidence-copy">
          选择资料或检索结果后，此处展示版本、来源、页码、条款与命中原文。
        </p>
        <dl>
          <div><dt>Authority</dt><dd>Catalog</dd></div>
          <div><dt>Locator</dt><dd>Page / Clause</dd></div>
          <div><dt>Index</dt><dd>FTS5 / BM25</dd></div>
        </dl>
      </aside>
    </div>
  </section>
</template>
