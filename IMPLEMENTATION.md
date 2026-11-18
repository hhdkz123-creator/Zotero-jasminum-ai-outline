# v1.1.45-ai.3 实施与验收记录

## 基线与移植

原仓库基于官方 1.1.44 提交 `9af49f7175d2257a15d1ee1598da893569510e29`，AI 每批 5 页扫描全书。本次根据用户后续指示改用官方 **v1.1.45 / d3b1b3227b0e46aaf56585c5c09ff9e343152ce4**，保留该版已有目录优先机制及其他官方功能；在其上应用增量补丁。

从本机现有定制代码迁移：常驻 AI/保存按钮、可换行工具栏、独立状态行、旋转图标、暂停/继续、静默自动保存、自动识别开关及按钮图形。保留现有 OpenAI 兼容调用协议和配置，保留本机主配置的模型、URL、凭据。真实文献先用副本验证，再通过插件正式保存入口更新目标文献，保留原件备份。

## 实际源码改动（相对于官方 v1.1.45）

所有源代码变更在 `patches/smart-outline-v1.1.45.patch`，以下路径为应用补丁后的上游工程路径。

| 文件 | 改动 |
| --- | --- |
| `src/modules/outline/recognitionAgent.ts` | 本地优先、5/15/30 页渐进探测、完整模式、早停、统一扫描缓存、跨重启导入/导出、请求额度和真实用量统计 |
| `src/modules/outline/localTOC.ts`（新增） | 本地目录行与层级解析、逐标题全文本地定位、罗马/页码重置/局部偏移直接定位 |
| `src/modules/outline/tocAgent.ts` | 复用官方页码投票/抽样；较长前置材料校准，抽样标题及页码联合验证 |
| `src/modules/outline/pdfAdapter.ts` | 本地文字批次缓存，避免重复提取相同页面 |
| `src/modules/outline/task.ts` | 同一任务状态及用量接口、已有大纲保护、缓存身份验证、PDF 改动检查、自动保存及重试 |
| `src/modules/outline/safeState.ts`（新增） | 文件摘要、mtime/大小验证、独立备份与失败回滚 |
| `src/modules/outline/taskView.ts` | 静默入口、准确阶段/用量订阅、保存重试、显式追加请求额度 |
| `src/modules/outline/index.ts` / `style.ts` | 移植常驻按钮及布局、旋转、暂停状态行、阶段和用量、完成恢复 |
| `src/modules/outline/auto.ts`（新增） | 移植自动识别开关及按钮图形，自动入口允许本地零配置识别 |
| `src/modules/outline/savePDF.ts` | 可选期望文件状态，worker 生命周期和超时 |
| `src/modules/workers/index.ts` / `outline.ts` | 传递并检查文件状态，去除包含页面/大纲数据的调试日志 |
| `src/utils/llm.ts` | 可选实际 usage 回调、无隐藏 HTTP 重试、HTTP 错误去敏；请求协议、模型和认证沿用 |
| `addon/prefs.js` / `typings/prefs.d.ts` | 模式、额度、自动识别开关及类型 |
| `addon/chrome/content/preferences-main.xhtml` / 三语言 `preferences-main.ftl` | 模式、额度设置与开关标签 |
| `test/outline_*_test.cjs` / `test/smart/*.cjs` | 适配原测试 fixture，新增智能识别、缓存、额度、数据保护测试 |

新增 `src/modules/notifier.ts` 启动补初始化：在注册正式阅读器事件后，等待已存在阅读器就绪并接入同一大纲初始化函数，避免主配置恢复标签页早于插件注册时缺少按钮。新增两项回归测试，分别覆盖已恢复页面及用户关闭大纲功能的情况。

官方 `heading.ts`、`buttonIcon.ts`、`src/utils/task.ts` 及 `src/modules/progress.ts` 保持 v1.1.45 实现。任务仍走官方 TaskRunner 队列、取消/重试与 Progress 通知，通过 `taskView.ts` 订阅更新静默侧栏，避免另建一套任务系统。

仓库级改动：`patches/patch_smart_outline.py` 校验固定基线并应用补丁；`patch_jasminum_release_metadata.py` 更新版本/品牌；`.github/workflows/build-release.yml` 加入锁定依赖、测试、打包验证和不覆盖 Release 的发布流程；`build-support/pnpm-lock.yaml` 固定依赖；`tests/run-tests.py`、`tests/prepare-xpi.py`、`tests/native/` 提供重现入口；README 和发行说明更新。

## 验证与证据范围

- 自动化：14 个上游 CJS 回归套件，加新增 29 项智能识别测试；全部通过。
- 关键案例：297 页目录本地 0 请求、扫描目录提前结束、297 页无目录及完整模式 60 请求/297 图片、复杂页码、目录不完整/双栏拒绝不可靠本地结果、抽样不符回退、取消/网络中断、缓存恢复、额度、无 usage 不虚构 token、已有大纲保护、文件外改、保存回滚。
- TypeScript `tsc --noEmit` 与 XPI 构建通过。最终安装包验证版本 1.1.45.3、插件 ID、名称、ZIP 完整性、使用本仓库空更新清单，并输出 SHA256。
- Zotero 10.0.9/macOS 隔离实例：真实侧栏 AI 按钮 → 本地文字提取/实际页面渲染 → HTTP 模拟返回 → 自动写入 PDF/sidecar → 书签读取和导航。297 页本地路径 0 请求；297 页扫描路径 5 请求/20 图片；完整模式 17 页为 4 请求并保存。验证三级层级和 PDF 144、294 页的书签目标、点击真实标题跳转至 144 页、按钮恢复、备份、重复保护、额度暂停与重启缓存恢复。
- 设置控件通过真实 command/change 事件写入模式和数字额度，再次重启核对保留。

本轮故障修复（ai.3）：

- `pageGeometry.ts` / worker：规范化反向页面框后计算交集，修复有效 PDF 渲染前失败。
- `tocAgent.ts`：阿拉伯正文投票排除目录前序言页码重置；保留独立锚点、正文矛盾拒绝及抽样验证。
- `recognitionAgent.ts` / `llm.ts`：准确报告安全的桥接错误，超时明确暂停并保存下一批大小，再次继续才缩批；复用每页缓存。优先使用已有完整 AI 目录，不被较弱的本地候选替代。
- `task.ts` / `taskView.ts` / `index.ts`：模式冲突非模态选择；切换保留缓存；阶段、累计图片与去重页统计准确；成功后仍保留更新身份的缓存；全功能模式设置保留。
- `test/smart/repair.test.cjs`：新增八项反向页面框、序言重置、正文冲突、504 缩批、缓存迁移、模式选择及脱敏错误测试。

真实 Zotero 10.0.9 隔离副本、实际模型与接口测试：297 页原著复用旧 29 页响应，新增仅一次请求/一张第 180 页图片，另一末尾样本本地验证；54 条实际目录写入 PDF 和 sidecar，逐条目的地检查、实际第 180 页点击通过。旧缓存中的层级仅 1/2，因此不声称已提取不存在的三级。8 页真实反向 MediaBox PDF 在完整模式两批（5+3 页）识别、自动保存成功。75 项实机断言通过，代理禁止重复发送成功页，实际无拦截。模型接口没有 token usage，不虚构数值。真实文献、缓存和凭据不随源码公开。

## 仍需真实文献验收

视觉模型的多栏/换行/漏目识别，极端罗马/重置/局部偏移，目录只列一级时用户所需的三级细节，PDF 特殊表单/签名与其他 Zotero 版本。抽样有覆盖边界，不能证明每个未采样页面没有插页；不确定时会全文兜底，受额度上限保护。PDF 与 sidecar 不具跨文件原子事务，崩溃和极短跨进程写入竞争仍需依靠备份恢复。
