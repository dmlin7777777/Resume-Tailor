# Phase 3 — Dynamic Interaction 执行细则（CP3 追问 / CP4 语调与边界 / 推断项确认）

> 本文件由 SKILL.md 拆分而来（Progressive Loading Protocol）。进入对应阶段时必读；SKILL.md 中的 🔴 STOP / Anti-Patterns 铁律全程有效。

**CP3 Progressive Probing Protocol** (when a bullet lacks quantification):

| Round | Question | Example |
|-------|----------|---------|
| 1 (Scope) | "影响了多少人/多少业务线？" | "全公司使用" / "覆盖 3 个 BU" |
| 2 (Comparison) | "改造前后分别是什么状态？用了多久？" | "从 48h 缩短到 12h" |
| 3 (Quality) | "准确率、错误率、客户反馈有变化吗？" | "准确率 99.5%" |
| 4 (Business Impact) | "为公司节省了多少钱/带来多少收入？" | "年节省 2000+ 小时" |

**If user cannot quantify after 2 rounds**: Write process-focused content, never use vague fillers ("实现智能化", "显著提升效率").

**CP4 Cultural Tone Slider**:

| Region | Level | Style | Self-Promotion |
|--------|-------|-------|----------------|
| North America | 5 (Assertive) | Led, Drove, Spearheaded | Results-first |
| UK/Ireland | 4 | Delivered, Managed | Measured confidence |
| DACH | 3 | Contributed to, Responsible for | Fact-focused |
| East Asia | 2 (Collaborative) | 协同, 推进, 支持 | Team-oriented |
| Nordics | 1 (Humble) | Contributed, Improved | Impact-only |

**CP4 Wording Boundary（硬边界 — 措辞升级只改形式，不改事实）**:

| ✅ 允许 | ❌ 禁止 |
|--------|--------|
| 换更强的动词（"参与了"→"主导了"）——**需有故事库/用户确认支撑** | 添加原简历和故事库里都没有的事实性描述 |
| 调整语气（弱→强，根据区域 slider） | 添加新的职责范围（如"覆盖从需求到上线的完整产品周期"——除非有依据） |
| 重组 bullet 结构（结果前置等） | 凭空添加量化数字 |
| 对齐 JD 关键词（原简历有对应概念时） | 为对齐 JD 编造不存在的经验 |
| 为每条 bullet 添加 `**前缀**:` 格式（命中 JD 关键词） | 前缀中使用形容词（"高效""全面""创新"） |

**🔴 如果对某条措辞升级是否越界存疑 → 输出 before/after 并标注「不确定是否有依据」，让用户确认后再写入。**

**🔴 推断项逐项确认规则**：CP4 中任何涉及 `[~]` 模型推断的内容（如 LLM 推断的部门名称、推断的技能水平、推断的业务规模），不能被用户的笼统回复（如"确认都可以""没问题"）通过。必须：
1. 在 CP4 输出中，推断项单独标注 `⚠️ [推断]` 前缀，与普通措辞升级视觉区分
2. 明确要求用户逐项确认推断内容的准确性（如"以下 2 条包含我推断的信息，请逐条确认"）
3. 用户确认后，推断项的 `info_status` 从 `inferred` 变为 `confirmed`；用户否认则删除该内容

**Global Interaction Principle**: Every question must include a concrete recommendation. User confirms or overrides — never decides from scratch.
