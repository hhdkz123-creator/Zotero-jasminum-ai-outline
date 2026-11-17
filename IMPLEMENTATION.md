# v1.1.45-ai.1 实施与验收记录

## 基线与移植

原仓库基于官方 1.1.44 提交 `9af49f7175d2257a15d1ee1598da893569510e29`，AI 每批 5 页扫描全书。本次根据用户后续指示改用官方 **v1.1.45 / d3b1b3227b0e46aaf56585c5c09ff9e343152ce4**，保留该版已有目录优先机制及其他官方功能；在其上应用增量补丁。

从本机现有定制代码迁移：常驻 AI/保存按钮、可换行工具栏、独立状态行、旋转图标、暂停/继续、静默自动保存、自动识别开关及按钮图形。保留现有 OpenAI 兼容调用协议和配置，未修改本机主配置的模型、URL、凭据或文献。

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

官方 `heading.ts`、`buttonIcon.ts`、`src/utils/task.ts` 及 `src/modules/progress.ts` 保持 v1.1.45 实现。任务仍走官方 TaskRunner 队列、取消/重试与 Progress 通知，通过 `taskView.ts` 订阅更新静默侧栏，避免另建一套任务系统。

仓库级改动：`patches/patch_smart_outline.py` 校验固定基线并应用补丁；`patch_jasminum_release_metadata.py` 更新版本/品牌；`.github/workflows/build-release.yml` 加入锁定依赖、测试、打包验证和不覆盖 Release 的发布流程；`build-support/pnpm-lock.yaml` 固定依赖；`tests/run-tests.py`、`tests/prepare-xpi.py`、`tests/native/` 提供重现入口；README 和发行说明更新。

## 验证与证据范围

- 自动化：14 个上游 CJS 回归套件，加新增 19 项智能识别测试；全部通过。
- 关键案例：297 页目录本地 0 请求、扫描目录提前结束、297 页无目录及完整模式 60 请求/297 图片、复杂页码、目录不完整/双栏拒绝不可靠本地结果、抽样不符回退、取消/网络中断、缓存恢复、额度、无 usage 不虚构 token、已有大纲保护、文件外改、保存回滚。
- TypeScript `tsc --noEmit` 与 XPI 构建通过。最终安装包验证版本 1.1.45.1、插件 ID、名称、ZIP 完整性、使用本仓库空更新清单，并输出 SHA256。
- Zotero 10.0.9/macOS 隔离实例：真实侧栏 AI 按钮 → 本地文字提取/实际页面渲染 → HTTP 模拟返回 → 自动写入 PDF/sidecar → 书签读取和导航。297 页本地路径 0 请求；297 页扫描路径 5 请求/20 图片；完整模式 17 页为 4 请求并保存。验证三级层级和 PDF 144、294 页的书签目标、点击真实标题跳转至 144 页、按钮恢复、备份、重复保护、额度暂停与重启缓存恢复。
- 设置控件通过真实 command/change 事件写入模式和数字额度，再次重启核对保留。

扫描 PDF 的 AI 返回、token usage 均为确定性 HTTP fixture，未向真实模型发送测试文献。因此“5 次/20 图”证明识别策略及端到端接通，不代表任意学术著作的 OCR/目录准确率或真实 GPT/Codex 扣费。具体那份约 297 页著作尚未提供，本次没有对其作模型准确率验收。主 Zotero 安装与原文献未替换。

## 仍需真实文献验收

视觉模型的多栏/换行/漏目识别，极端罗马/重置/局部偏移，目录只列一级时用户所需的三级细节，PDF 特殊表单/签名与其他 Zotero 版本。抽样有覆盖边界，不能证明每个未采样页面没有插页；不确定时会全文兜底，受额度上限保护。PDF 与 sidecar 不具跨文件原子事务，崩溃和极短跨进程写入竞争仍需依靠备份恢复。
