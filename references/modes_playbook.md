# Modes Playbook — Scenario C/D · Mode A2 · Mode B · Story Library Protocol

> 本文件由 SKILL.md 拆分而来（Progressive Loading Protocol）。进入对应阶段时必读；SKILL.md 中的 🔴 STOP / Anti-Patterns 铁律全程有效。

### Scenario C: JD-Only（有 JD 无简历）

用户提供了 JD 但没有简历（`resume_master.md` 不存在且用户未提供任何简历文件）。

**与 Init-A 的区别**：Init-A 是"用户没有格式化简历但有经历可录入"。Scenario C 是"用户先拿到 JD，想知道要准备什么，再决定怎么写简历"。

**Flow**:

```
Step C1: JD 需求分析（复用 Phase 1 Scout）
  - 提取 JD 的 hard/soft requirements、capability clusters、ATS keywords
  - 执行 S1 面经搜索（如果公司已知）
  - 产出「岗位需求清单」：每项需求标注优先级（必须/加分/锦上添花）

Step C2: 能力缺口预判
  - 输出：「以下是这个岗位的核心要求，你可以对照看看自己有哪些：」
  - 逐项列出需求，让用户标注 ✅有 / ❌没有 / 🤔不确定
  - 🔴 STOP：等待用户回复

Step C3: 路由决策
  - 用户标注完成后：
    ├─ ✅ 命中率 ≥ 50% → 「你的匹配度不错，我们来创建简历。」→ 进入 Init-A，完成后自动进入 Mode A
    ├─ ✅ 命中率 < 50% → 「这个岗位和你的背景差距较大，建议：(1) 继续做，突出可迁移能力 (2) 换一个更匹配的方向」
    └─ 用户选择继续 → Init-A → Mode A
```

### Scenario D: 信息不足（输入模糊或极度不足）

用户输入过于模糊，无法判断任何 Mode。

**触发条件**：输入 < 20 字 且 不包含 JD/简历/方向关键词。例如："帮我弄一下"、"简历"、"resume"。

**Flow**:

```
输出：「我需要更多信息来帮你。请告诉我：
  1. 你有目标岗位的 JD 吗？（有 → 粘贴 JD 文本或链接）
  2. 你有现成的简历吗？（有 → 提供文件路径或粘贴内容）
  3. 你想做什么？
     - 针对特定岗位优化简历 → 需要 JD + 简历
     - 做个通用方向简历 → 需要简历 + 目标方向
     - 从头创建简历 → 我来引导你
     - 分析一个 JD 的要求 → 只需要 JD」
→ 等待用户回复后重新进入 Mode Detection
```

**约束**：Scenario D 最多触发一次。用户第二次回复仍然模糊 → 默认进入 Init-A（从头创建简历），不再追问。

### Mode A2: Multi-JD Batch（多 JD 批量定制）

同一份事实底稿（`resume_master.md` + 故事库），针对多个 JD 各生成一份定制简历，最后产出跨 JD 差异对比表。

**核心原则：共用事实底稿 + 独立版本 + 差异表**

**Trigger**:
- 用户一次提供 ≥2 份 JD
- Mode A 完成后追加新 JD（升级路径）

**Flow**:

```
Phase A2-0: JD Collection & Naming
  1. 收集所有 JD（文本/URL/文件），每份 JD 分配标签：JD-A, JD-B, JD-C...
  2. 展示 JD 摘要表（岗位名 + 公司 + 核心要求 3 条），用户确认无误
  3. 🔴 STOP：确认 JD 列表完整，后续追加需重新进入此步骤

Phase A2-1: Shared Context（共享层，只做一次）
  1. 读取 resume_master.md + 故事库（如有）
  2. 对所有 JD 执行合并式 Scout：提取每份 JD 的 hard/soft requirements
  3. 产出「能力需求联合矩阵」：行=用户经历，列=各 JD 的需求，交叉格=匹配状态
  4. 🔴 STOP CP1-A2：展示联合矩阵 → 用户确认经历选取策略
     - 哪些经历所有 JD 通用
     - 哪些经历只用于特定 JD

Phase A2-2: Per-JD Tailoring（逐份独立执行）
  对每份 JD，独立运行 Mode A 的 Phase 2-4：
  - 独立 session_id：{date}_{company}_{role}
  - 独立 snapshot.json
  - 复用 A2-1 的共享选取决策，但允许 per-JD 微调
  - CP3 量化追问：如用户在 JD-A 中已回答某数字，JD-B 自动复用（标注「来源：JD-A session」）
  - CP4 措辞：根据各 JD 的 region 独立调整 tone slider

Phase A2-3: Comparison Table（差异对比表）
  所有 JD 完成后，产出对比表：

  | 维度 | JD-A ({company_a}) | JD-B ({company_b}) |
  |------|-------|-------|
  | 匹配度 | 85% | 72% |
  | 保留经历 | 经历1,2,3 | 经历1,3,4 |
  | 核心差异 bullet | "数据分析"侧重 | "产品运营"侧重 |
  | 硬缺口 | 无 | 缺 CPA 证书 |
  | 推荐投递优先级 | ⭐⭐⭐ | ⭐⭐ |
  | tone 风格 | 北美-assertive | 东亚-collaborative |

  保存到 history/{date}_multi_jd_comparison.md
```

**关键约束**：
- 事实底稿（resume_master.md）全程不可修改——所有 JD 共享同一份源
- 量化数据跨 JD 复用：用户在 JD-A 确认的数字，JD-B 自动继承，避免重复追问
- 每份 JD 的 Auditor 独立运行——不能因为 JD-A 审计通过就跳过 JD-B 的审计
- Phase A2-2 中的 per-JD tailoring 可以并行执行（如果 Agent 支持）


### Mode B: General-Purpose（无 JD 通用）

Simplified pipeline when no specific JD is available. Builds a role-oriented resume using capability matching from the story library.

**Trigger**:
- User asks for a resume "for X role" without providing a JD
- "帮我针对产品岗位生成一个通用性的简历"
- "做个通用版简历" / "make a general resume"
- "生成XX方向的简历" / "create a role-oriented resume"

**Flow**:

```
Phase G1: Capability Matching (replaces Phase 1+2)
  1. Identify target role type from user's description (e.g., 产品/数据/商业分析)
  2. Read project story library (唯一事实来源) → follow [[#Story Library Protocol]] for token-efficient extraction
  3. Build capability matching matrix: experience × core role competencies (numbers MUST come from story library)
  4. Rank experiences by match score
  5. Present selection recommendation to user (CP1)

Phase G2: Interactive Refinement (= Phase 3, CP1-CP4)
  **🔴 STOP CP1**: Experience selection → show ranked list → **WAIT for user picks**
  CP2: Skipped (no JD → no gap analysis)
  **🔴 STOP CP3**: Quantification audit (Anti-Filler Rule) → **WAIT for user to confirm or provide numbers**
  **🔴 STOP CP4**: Wording upgrade → show before/after → **WAIT for user approval**

Phase G3: Delivery & Audit (= Phase 4)
  Same physical isolation audit as Mode A.
  Additional Auditor check: "Does this bullet claim something not in the story library?"
```

**Key Differences from Mode A**:
- No JD → No `jd_facts` layer, no ATS keyword matching, no hard requirement alerts
- Story library is the **sole source of truth** — no fabrication, no speculation, no "logical inference"
- If story library lacks data for a bullet → ask user to confirm, never invent
- Simpler matching: role-type competencies instead of JD-specific keywords

**⚠️ Critical Rule for Mode B**: 
> **只做提炼，不做扩展。** Even logically reasonable inferences (e.g., "覆盖从需求定义到上线的完整周期") are FORBIDDEN unless explicitly stated in the story library. Only distill and reorganize what already exists.

## Story Library Protocol（Mode B 专用）

故事库是 Mode B 的唯一事实来源。不读故事库 = 不能生成 Mode B 简历。

### 故事库结构

故事库是一个结构化 Markdown 文件（通常位于 Obsidian vault 或 workspace 中），结构如下：

```
## 项目 N：名称
│
├── > 技术栈：...           ← 工具关键词
├── > 一句话概括：...        ← Phase G1 初筛用这个
├── ### NA：子项目名         ← 每个子项目 = 一段经历
│   ├── STAR（S/T/A/R）     ← 简历 bullet 的法定来源
│   ├── 高频追问准备         ← CP3 量化审计 + Phase 4 审计用
│   └── 方案选择与决策逻辑    ← 面试深度素材
└── ### 面试高频追问          ← 项目级追问
```

### 读取策略（Token高效，分 3 层递进）

**Layer 1 — 扫描标题（`grep "^## 项目"`）**
只读项目编号和名称，不看正文。目的：知道故事库覆盖了哪些经历、缺失哪些。

**Layer 2 — 初筛匹配（读 `> 一句话概括` + `> 技术栈`）**
对目标岗位相关的项目，只读一行概括。目的：2 秒判断这个项目要不要放进简历。

**Layer 3 — 深读（读完整 STAR + 追问）**
对确认入选的项目，读完整子条目。目的：提取真实的 bullet 措辞和量化数据。

❌ **禁止**：一次性读取整个故事库 → 浪费 token 且 Agent 注意力衰减。

### Phase G1：能力匹配矩阵

从 Layer 2 的一行概括中提取每段经历的：
- **核心动作**（做了什么）
- **量化结果**（数字是什么）
- **工具**（技术栈关键词）

然后对目标岗位的核心能力（如数据分析师 = SQL/Python/可视化/AB测试/ETL）逐项打分。**匹配矩阵中的数字必须来自故事库，不能编造。**

### Phase G2 CP3：量化审计

故事库中每个子项目的 STAR "R" 行是量化数据的唯一来源。CP3 追问时：
- 如果故事库已经有数字 → 直接用
- 如果故事库没数字 → 问用户
- 如果用户也答不出 → 用过程描述替代，**绝不编造**

### Phase G3 审计：故事库交叉验证

Auditor 逐条检查每个 resume bullet：“这个 bullet 能在故事库中找到对应证据吗？”

| 审计结果 | 含义 | 处理 |
|---|---|---|
| ✅ 故事库有对应 STAR | 证据充足 | 通过 |
| ⚠️ 故事库有对应条目但 bullet 措辞偏离 | 需要修正 | 回退 CP4 重写 |
| 🔴 故事库无此条目 | 无法面试辩护 | **删除该 bullet** 或让用户手动补故事库 |

