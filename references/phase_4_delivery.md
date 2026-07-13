# Phase 4 — Delivery & Audit 执行细则（4a-4f · 渲染管线 · PDF）

> 本文件由 SKILL.md 拆分而来（Progressive Loading Protocol）。进入对应阶段时必读；SKILL.md 中的 🔴 STOP / Anti-Patterns 铁律全程有效。

### Phase 4: Delivery & Audit (Physical Isolation)

**Two separate LLM calls — this is the critical architectural guarantee.**

**单 Agent 降级方案**：当运行环境不支持独立 LLM 调用（如 Claude Code 单 session、Cursor 单窗口）时，Writer 和 Auditor 无法真正物理隔离。此时采用以下降级措施：
1. Writer 完成草稿后，Auditor 必须**重新阅读源简历和 JD 作为首要输入**，不引用 Writer 的推理过程
2. Auditor 的审计日志必须写入独立文件，不与草稿混在同一输出中
3. 在审计日志中标注 `isolation_mode: degraded`，表示本次审计在共享上下文中完成

#### Step 4a: Writer Node — Generate Draft

**Node**: Resume Architect (`architect_writer`)
**Formatting**: `references/formatting_rules.md` (contact info, certifications, bullet writing, skills section)
**Input**: All confirmed decisions from Phase 3
**Action**: Generate Markdown draft, save to `history/YYYY-MM-DD_{company}_{role}.md`
**Constraint**: DO NOT self-audit. Just produce the draft.
**🔴 交付物禁止标记泄露**：Writer 输出的 Markdown 草稿是最终交付物的基础，**禁止**在 bullet 中写入 `[✓]`、`[?]`、`[~]` 等信息状态标记。这些标记仅存在于 snapshot 的 `confirmed_quantifications` 字段和审计日志中，不出现在简历正文。

**🔴 Bullet 格式硬规则**：工作经历和项目经历中的每一条 bullet **必须**使用 `**前缀**: 详细内容` 格式。前缀 2-4 个词，命中 JD 关键词，不含形容词。

```markdown
✅ 正确（中文）：
- **数据监控体系**：搭建外卖业务核心指标看板（Tableau），覆盖30+指标
- **AB 测试优化**：主导3次 A/B 测试设计与分析，推动订单转化率提升8%

✅ 正确（英文）：
- **KPI Monitoring:** Built a real-time capital operations monitoring system, consolidating 15 SQL scripts into a unified dashboard covering 10+ metrics
- **Process Automation:** Automated reconciliation between computed Net Position and system-native Net Unbilled WIP — reduced monthly close from 48h to 12h (↓75%)

❌ 错误：
- 搭建了外卖业务核心指标看板（Tableau），覆盖30+指标     ← 缺 **前缀**:
- **高效搭建数据看板**：...                                ← 前缀含形容词"高效"
- Architected a FIFO-based rolling aging model in Power BI... ← 英文 bullets 也需要 **Prefix**: 格式
```

无 `**前缀**:` 的 bullet = Auditor 4c 自动标记 🟡 MINOR 格式违规。

#### Step 4b: Auditor Node — Compliance Check

**Node**: Sincerity Auditor (`auditor_compliance`)
**Input**: Draft + target region rules
**Action**: Regional compliance (photo, age, PII per region)
**Output**: Compliance table with 🔴 critical violations

#### Step 4c: Auditor Node — Reverse Audit

**Node**: Sincerity Auditor (`auditor_sincerity`)
**Input**: Draft + interviewer persona + JD context + **Phase 1 `interview_intel`（面经摘要 + 面试重点提示）**
**Actions**:
1. Construct senior interviewer persona based on role type **+ Phase 1 S1 面经中提取的面试官风格/高频考点**
2. Review every bullet for: AI trace, logical gap, scope inflation, buzzword defense, cultural mismatch, **`**前缀**:` 格式缺失**
3. Classify severity: 🔴 MAJOR / 🟡 MINOR / 🟢 INFO
   - 缺少 `**前缀**:` 格式的 bullet → 🟡 MINOR（格式违规，回退 Writer 补前缀）
4. For each 🔴 MAJOR: generate mock interview questions + STAR prep sheets
   - **Mock 问题优先取材自 Phase 1 S1 面经**：如面经中提到"面试官喜欢追问 AB 测试细节"，则 mock 问题必须覆盖 AB 测试场景

**If 🔴 MAJOR found**: Set flag `["ROLLBACK"]` in STATE_UPDATE → engine reverts to Phase 3. **🔴 STOP — report findings to user before rollback, let user decide which issues to fix.**

#### Step 4d: Compile & Deliver

1. Run `scripts/diff_audit.py` (source vs tailored change evidence)
2. Run `scripts/ats_checker.py` (ATS compatibility score)
3. Compile final audit log combining all sources
4. Save Markdown draft: `history/{date}_{company}_{role}.md`
5. Render HTML: 将 MD 内容按节段映射到 `templates/resume_swiss.html` 模板变量 → 写入 `history/{date}_{company}_{role}.html`
5b. **🔴 单页容量自检（Single-Page Fit Check，强制）**：一页简历必须打印在 A4 单页内，不允许某个 section（尤其 PROJECTS/SKILLS）被挤到第二页。
   - **统计正文 bullet 总数**（所有经历 + 项目的 `<li>` 之和）+ 经历/项目条目数。
   - **按内容量选 density**（写入 `<body data-density="...">`，CSS 全文仍逐字节照抄模板，仅此一个属性可变）：
     | 正文 bullet 数 | density 属性 | 说明 |
     |---|---|---|
     | <= 10 | `relaxed` | 内容少，放宽间距更美观 |
     | 11 - 16 | *(默认，不加属性)* | 模板默认已是单页安全基线 |
     | 17+ | `ultra` | 极限压缩，最后手段；优先考虑精简 bullet |
   - **交付时 Agent 已同时产出 PDF**（字体子集化，< 500KB，见 Step 4d-5c），用户无需手动 Ctrl+P。仍提示用户可在浏览器打开 HTML 复核排版；若某节换页，回我一声我再收紧 density。
5c. **🔴 生成 PDF 交付物（强制）**：调用 `scripts/gen_resume_pdf.py {date}_{company}_{role}.html {date}_{company}_{role}.pdf` 产出字体子集化 PDF（目标 < 500KB、A4 单页）。若环境缺 playwright/pymupdf → 降级为用户手动 Ctrl+P 并在交付中明确警告字体膨胀风险（见 Rendering Pipeline 的 PDF 管线说明）。PDF 与 HTML 同路径同前缀，一并交付。
6. Archive snapshot from `sessions/` to `history/`

> 🛑 **DELIVERY GATE**：Phase 4a Writer → Phase 4b Compliance → Phase 4c Reverse Audit（含 B-3 编造阻断门） → Phase 4d Compile → Phase 4e Historical Audit → Phase 4f Interview Prep，**六步缺一不可**。跳过 Auditor = 未完成交付。编造阻断门任一 🔴 → 整份草稿 ROLLBACK。跳过 4f = 交付不完整。

#### HTML 模板变量映射

`templates/resume_swiss.html` 使用 `{{VARIABLE}}` 占位符，渲染时替换：

| 模板变量 | 来源 | 说明 |
|---------|------|------|
| `{{NAME}}` | resume_master.md 个人信息 → 姓名 | 顶部大标题 |
| `{{SUBTITLE_BLOCK}}` | 目标岗位 / 一句话定位 | 可选，无则留空 |
| `{{CONTACT_ITEMS}}` | 邮箱、电话、城市、LinkedIn、GitHub | 各一个 `<span>` |
| `{{SUMMARY_BLOCK}}` | 个人总结段 | 可选，无则留空（含 section-title + 段落） |
| `{{EDUCATION_SECTION}}` | 教育背景整节（标题 + 条目） | 每个学历 = 一个 `.edu-item` |
| `{{EXPERIENCE_SECTION}}` | 工作经历整节（标题 + 条目） | 每个经历 = 一个 `.exp-item` |
| `{{PROJECTS_SECTION}}` | 项目经历整节 | 可选，结构与 experience 相同 |
| `{{SKILLS_SECTION}}` | 技能整节（标题 + skills-grid） | 每个 skill = 一个 `.skill-entry` |
| `{{META_EXTRA}}` | 公司名、日期等元信息 | 非打印区生成信息 |

#### Output Naming Convention

- **项目副标题**：写角色/身份（如"独立开发""个人项目"），**不写课程编号或学校名**（如 ❌"NUS BAP" ❌"课程项目"）。目的是让面试官感知为独立成果而非课堂 toy。
- **地点**：写城市或国家，不写学校。

#### Step 4e: Historical Version Audit ⭐

**每次生成新简历前，必须与历史版本对比。不允许新版本在量化或措辞上比旧版倒退。**

**执行时机**：Phase 4d 编译完成后、交付用户前。

**操作步骤**：
1. `find history/ -name "*.html" -o -name "*.md" | sort -r | head -3` — 取最近 3 份历史简历
2. 逐段对比新简历 vs 最近版本：

| 检查维度 | 方法 | 触发条件 |
|---|---|---|
| **量化倒退** | grep 新简历的每个数字（百分比/时长/金额），确认旧版同 bullet 有该数字 | 旧版有量化数据而新版删除了 → 🔴 |
| **内容回退** | 对比同经历的 bullet 数量和覆盖维度 | 旧版 4 条 bullet 新版 3 条，且缺失的不是刻意删除的 → 🟡 |
| **措辞弱化** | 对比同 bullet 的动词（如"主导"变"参与"、"设计"变"协助"） | 动词降级且无合理解释 → 🟡 |

**处理规则**：
- 🔴 量化倒退 → **必须回退到旧版数字**，除非用户明确要求删除
- 🟡 内容回退/措辞弱化 → **列出差异给用户确认**，由用户决定保留新版还是回退
- 如果旧简历本身有错误（数字不对、经历过时），新版纠正不算倒退

**反例**：新版简历将旧版的"将处理时间从 X 缩短到 Y"简化为"显著提升效率"，丢失了具体量化数据——这就是量化倒退。本条 Protocol 的意义就是防止这类问题：新版本必须在每个维度上 ≥ 旧版本。

3. 输出审计报告：`{date}_{role}_version_audit.md`，列出所有差异及处理建议
4. 🔴 STOP — 展示差异给用户确认后再交付

#### Step 4f: Interview Prep Pack（面试准备包）

**这是标准交付物，不是可选项。** 每次 Mode A/A2 交付都必须包含面试准备包。

**Node**: Sincerity Auditor（复用 Phase 4c 的面试官人设）
**Input**: 
- Final draft（4e 审计通过后的版本）
- Phase 1 `interview_intel`（S1 面经情报）
- `resume_master.md`（原始简历，用于识别"显著变化"）

**步骤**：

1. **识别显著变化**：对比 `resume_master.md` 和最终简历，提取所有：
   - 新增的 bullet（CP2 缺口填补产生的新内容）
   - 量化数据发生变化的 bullet（CP3 追问后补充了数字）
   - 措辞显著升级的 bullet（CP4 动词等级提升 ≥2 级）

2. **为每个显著变化生成面试 QA**：

   ```markdown
   ### [经历名称] — [变化类型：新增/量化补充/措辞升级]

   **简历写法**：[最终简历中的 bullet]
   **与原始简历的差异**：[改了什么]

   **面试官可能追问**：
   1. [问题 1]（来源：Phase 1 面经 / 通用追问模式）
   2. [问题 2]

   **STAR 应答要点**：
   - S（背景）：[情境]
   - T（任务）：[目标]
   - A（行动）：[你的具体行动]
   - R（结果）：[量化结果 + 数据来源]

   **⚠️ 面试注意**：[需要特别留意的点，如数字来源、角色边界、避免过度包装]
   ```

3. **通用高频问题**（基于 S1 面经）：
   - 从 Phase 1 S1 面经中提取出现频率最高的 3-5 个追问方向
   - 每个方向给出 1 个典型问题 + 应答建议
   - 如 S1 面经抓取失败（降级到 L4），则基于岗位类型生成通用问题，标注「来源：通用模板（面经抓取失败）」

4. **展示 + 保存**：
   - 🔴 STOP — 面试准备包展示给用户，作为交付物的一部分
   - 保存到 `history/{date}_{company}_{role}_interview_prep.md`

**与 Phase 4c 的关系**：
- 4c 是审计：找问题、判断是否 ROLLBACK，mock 问题仅针对 🔴 MAJOR 风险点
- 4f 是面试准备：覆盖所有显著变化，帮用户准备回答
- 4c 的 mock 问题是防御性的（"这个 bullet 可能被追穿"），4f 的 mock 问题是建设性的（"面试官会问什么，怎么答"）

## Rendering Pipeline

```
Phase 4a Writer → {date}_{company}_{role}.md （Markdown 草稿，始终产出）
                    │
                    ├──→ 直接交付 Markdown
                    │    可读、可 diff、可进 Git 版本审计
                    │    这是简历的「源代码」——所有渲染格式由此衍生
                    │
                    ├──→ 模板替换 → {date}_{company}_{role}.html （主交付物）
                    │    模板：templates/resume_swiss.html
                    │    渲染方式：renderer.py 解析 MD，填充 {{SECTION}} 级占位符
                    │    Times New Roman 传统风，单文件自包含，零外部依赖
                    │
                    └──→ 字体子集化 → {date}_{company}_{role}.pdf （主交付物，Agent 自动产出）
                         管线：scripts/gen_resume_pdf.py（Playwright 无头渲染 + PyMuPDF 字体子集化压缩）
                         目标体积 < 500KB（一页纯文本简历正常 ~100KB），A4 单页，内容无损
                         浏览器打开 HTML 复核排版为可选，不再强依赖手动 Ctrl+P
```

**输出优先级**：

| 格式 | 优先级 | 说明 |
|------|--------|------|
| **Markdown** | 主交付物 | Phase 4a Writer 直接产出，可读、可 diff、可进 Git 版本审计。这是简历的「源代码」 |
| **HTML** | 主交付物 | `templates/resume_swiss.html` 模板渲染，Times New Roman 传统风，浏览器直接打开 |
| **PDF** | 主交付物 | `scripts/gen_resume_pdf.py` 自动产出（Playwright 无头渲染 + PyMuPDF 字体子集化压缩），目标 < 500KB、A4 单页；浏览器 Ctrl+P 复核为可选 |
| DOCX | 已移除 | v3.3 起不再作为 pipeline 步骤，移除 WeasyPrint / pandoc / pypandoc 依赖 |

**HTML 模板设计原则**（Times New Roman 传统风）：
- 衬线标题体 + 微软雅黑后备，信噪比优先
- 粗体冒号前缀 bullet 格式（`<span class="bullet-summary">前缀：</span> 描述`）
- 单文件自包含，CSS 变量驱动，零外部依赖
- A4 打印优化：`@page { size: A4 }` + `print-color-adjust: exact`
- 字体：Times New Roman (Latin) + Microsoft YaHei / 微软雅黑 (CJK)

**🔴 Writer HTML 生成强制规则**：Writer 必须从 `templates/resume_swiss.html` 复制 `<style>` 标签全文（不含 `{{VARIABLE}}` 注释），嵌入生成的 HTML 中。禁止自定义 CSS、禁止替换字体、禁止修改设计 token。每次生成的 HTML 应与历史版本 CSS 逐字节一致。**唯一允许的例外**：`<body>` 标签可按 Step 4d-5b 的自检结果追加 `data-density="relaxed|ultra"` 属性来切换单页密度——这不改 CSS 本身（密度覆盖块已内建在模板 `<style>` 里），只是选择一档预设。禁止手改 `--fs-*`/`--gap-*`/`--lh-*` 等变量值。

**渲染降级**：
- 模板文件缺失 → 直接 Markdown 交付，HTML 生成跳过，不报错不中断
- **零依赖降级**：不需要任何 Python 包。renderer.py 仅使用 Python 标准库（json、re、pathlib）

**PDF 生成管线（Step 4d-5c，强制）**：
- **目的**：简历 PDF 必须 < 500KB、A4 单页、内容无损；**杜绝浏览器"另存为 PDF"把完整 TNR 字体嵌入导致 900KB+ 的问题**
- **脚本**：`scripts/gen_resume_pdf.py <input.html> <output.pdf>`
- **管线**：Playwright Chromium（无头）渲染 HTML → PyMuPDF `subset_fonts()` + `deflate=True` + `garbage=4` + `clean=True` 压缩
- **前置依赖**：`pip install playwright pymupdf`；`playwright install chromium`（浏览器缓存于 ms-playwright）
- **体积基线**：一页纯文本简历正常 ~100KB；若 > 500KB 触发告警
- **降级路径**：环境无 playwright/pymupdf → 回退提示用户手动 Ctrl+P，并明确警告「浏览器另存为 PDF 会嵌入完整 TNR 字体导致 900KB+，务必用 Chromium 无头或本管线」；交付中 PDF 行标注为「用户侧生成（未子集化）」

