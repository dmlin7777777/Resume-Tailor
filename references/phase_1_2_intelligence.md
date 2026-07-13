# Phase 1 & 2 — Contextual Intelligence + Strict Matching 执行细则

> 本文件由 SKILL.md 拆分而来（Progressive Loading Protocol）。进入对应阶段时必读；SKILL.md 中的 🔴 STOP / Anti-Patterns 铁律全程有效。

### Phase 1: Contextual Intelligence

**Node**: Context Scout
**Reference**: `references/writer_guide.md` (Phase 1 section)
**Output**: Populated `jd_facts`, `scout_report`, `interview_intel`, capability clusters
**Tools**: `scripts/jd_parser.py` (with graceful fallback to LLM), `web_search`

1. Accept JD input (URL → fetch, or text directly)
2. Ask user: company name? target region?
3. Run **结构化联网搜索**（3 轮分层，每轮产出必须落地到下游节点）：

| 轮次 | 搜索目标 | 关键词模板 | 产出落地点 |
|------|---------|-----------|-----------|
| **S1 — 面经/面试经验** | 面试官真实追问、高频考点、岗位隐性要求 | `"{公司} {岗位} 面经"` `"{公司} 面试 经验"` `"{岗位} 面试题"` `"{公司} {岗位} 面试 准备"` | → CP3 量化追问定向 + Phase 4c mock 问题真实性 |
| **S2 — 团队/文化/真实工作内容** | 部门风格、实际技术栈、JD 写的 vs 实际做的差距 | `"{公司} {部门} 工作体验"` `"{公司} 技术栈"` `"在 {公司} 做 {岗位} 是怎样体验"` | → Phase 2 技能匹配权重 + CP4 语气 slider 校准 |
| **S3 — 公司动态/业务重点** | 财报方向、新产品线、组织架构变动 | `"{公司} 202X 业务 重点"` `"{公司} 组织架构 调整"` `"{公司} 财报 分析"` | → `risk_warnings`（业务收缩部门标注）+ `capability_clusters` 定向 |

**搜索执行规则**：
- **S1 必须执行**：面经是简历定制的关键上下文，直接影响 CP3 追问方向和 Phase 4c mock 问题的真实性
- **S2 条件执行**：公司知名度高（大厂/独角兽/上市公司）→ 必须执行；小型/冷门公司 → 降级为可选，避免无结果
- **S3 按需执行**：用户表达了目标公司的长期发展关切，或公司近期有重大新闻/裁员/业务调整时触发
- **每轮搜索结果必须至少影响一项下游产出**（见"产出落地点"列），否则标记为无效搜索（违反 A6）
- 搜索结果中提取的关键信息标注 `来源：[搜索关键词]`，存入 `scout_report` 和 `interview_intel`

**搜索降级链（当 WebFetch/WebSearch 被拦截时）**：

| 降级层 | 工具 | 适用场景 |
|--------|------|---------|
| **L1（默认）** | WebSearch + WebFetch | 静态页面、大部分搜索引擎结果 |
| **L2（JS 渲染）** | agent-browser（`agent-browser open <url>` → `agent-browser snapshot`） | JS 动态加载、被 bot 检测拦截的页面 |
| **L3（真实浏览器）** | Claude in Chrome MCP（如 session 中可用） | 强反爬站、需要登录的站点 |
| **L4（降级兜底）** | 搜索摘要片段 | 所有抓取手段失败时，仅用搜索引擎返回的标题+摘要 |

**降级执行规则**：
- WebFetch 返回空/403/超时 → 用 agent-browser 重试同一 URL
- agent-browser 也失败 → 有 Chrome MCP 则用真实浏览器，无则跳到 L4
- L4 兜底：使用搜索引擎返回的摘要片段作为情报，在 `scout_report` 中标注 `来源：搜索摘要（原文抓取失败）`
- **不因为抓取失败就跳过整个搜索轮次**——摘要通常足够提取面经关键信息
- 降级状态写入 snapshot `_meta.search_degradation`，Auditor 可据此评估情报可靠性

4. Execute unified context extraction (script + LLM in one pass). Note: `jd_parser.py` only extracts structured features (years, degree). Scout must extract skill keywords, soft requirements, and `ats_keywords` via LLM and write them into `jd_facts` via STATE_UPDATE.
5. Detect role level, region, document type
6. Output consolidated context table + `interview_intel` 卡片（面经摘要 + 面试重点提示 + 文化关键词）+ risk warnings

### Phase 2: Strict Matching

**Node**: Context Scout (continuation) or Architect (if Fast-Track)
**Reference**: Integrated into Phase 1 or `references/writer_guide.md`

1. Read source resume (structured reader for .docx, fallback for .pdf)
2. Semantic matching: Direct + Implicit (with confidence) + Gaps
3. Cross-credential alignment
4. Match score calculation
5. Hard requirement alerts (dealbreakers)

**Match output must classify each JD requirement into one of 5 states:**

| State | Definition | Action |
|-------|-----------|--------|
| ✅ 已覆盖 | Direct, specific, verifiable evidence in resume | Polish wording at CP4 |
| 🟡 弱覆盖 | Related experience exists but lacks depth, specifics, or individual contribution | Probe at CP3 for quantification |
| ⬜ 未覆盖 | No evidence in current materials | Probe at CP3 for hidden experience |
| 🔍 可补充 | User likely has relevant experience not yet captured | Ask targeted questions at CP3 |
| ⛔ 不建议硬凑 | Clearly missing required credentials, industry, tools, or years of experience — no transferable path | Flag honestly. Tell the user: "这条不值得凑，硬写反而暴露缺口" |

**"不建议硬凑" judgment criteria:**
- Missing a hard credential (CPA, specific license, degree requirement)
- Missing required industry experience with no transferable overlap
- Missing required years of experience by a wide margin (e.g., JD asks 5+ years, user has 1)
- Required tool/framework the user has never used and cannot credibly claim

**This state is as important as "已覆盖" — telling the user what NOT to pursue saves them from interview exposure.**
