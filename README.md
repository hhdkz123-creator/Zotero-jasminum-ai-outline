# Zotero-jasminum-ai-outline

**Zotero 茉莉花 · AI 大纲优化版**（基于 [Jasminum](https://github.com/l0o0/jasminum) 1.1.44 的非官方衍生版本）

本仓库由上游指定提交 `9af49f7175d2257a15d1ee1598da893569510e29`、可公开审查的增量补丁及 GitHub Actions 构成，支持重新构建可安装的 XPI。

## 核心功能

- 点击 PDF 大纲工具栏中的 AI 图标后在后台识别，正常流程不再弹出遮挡文献的任务或核对窗口。
- 识别成功后自动保存 PDF 与茉莉花大纲；失败时显示具体错误。
- 将 AI 全文大纲识别按钮固定在大纲工具栏，不必展开「⋮」。
- 识别期间显示旋转图标及识别页数，写入时显示状态，成功后自动恢复。

## 安装和使用

1. 前往 [Releases](../../releases)，下载最新的 `.xpi` 安装文件。
2. 打开 Zotero → 工具 → 插件 → 齿轮 → 从文件安装插件，并按需重启 Zotero。
3. 在 Zotero → 设置 → 茉莉花 → AI 识别中填写 **支持图片输入的模型**、API Base URL 和 API Key。**这些信息不会上传到本仓库。**
4. 打开 PDF → 大纲侧栏 → 点击星光 AI 图标即可运行。

## 定制版版本规则（重要）

| 项目 | 值 |
| --- | --- |
| 项目名称、Zotero 插件显示名称 | `Zotero-jasminum-ai-outline` |
| GitHub Release | `v1.1.44-ai.2` |
| Zotero/Firefox 插件内部版本 | `1.1.44.2` |
| 插件 ID | `jasminum@linxzh.com`（保留上游 ID） |
| 更新方式 | 手动安装新版 XPI，已移除上游 `update_url` |

**为何内部版本是 `1.1.44.2`？** 扩展清单建议使用 1～4 段的数字版本号。保留上游插件 ID 时，数字版本 `1.1.44.2` 也比原版 `1.1.44` 高，方便同一 Zotero 安装进行替换；对外仍以 `ai.2` 标识定制发行版。

**为什么暂时禁用自动更新？** 定制版与官方原版使用同一个插件 ID，自动更新原版可能覆盖静默识别功能。待建立独立可靠的更新源后，才能安全启用定制版更新。后续版本需同步递增内部版本、发布标签和附件名称。

## 代码、构建与安全

[构建工作流](.github/workflows/build-release.yml) 从固定上游版本下载源码，然后依次执行：

- [静默识别与自动保存补丁](patches/patch_jasminum_silent_outline.py)
- [后台进度反馈补丁](patches/patch_jasminum_outline_progress.py)
- [版本和名称元数据补丁](patches/patch_jasminum_release_metadata.py)

使用 Node.js 22 与 pnpm 9.15.1 构建，随后验证 XPI 中的名称、数字版本号、插件 ID 及更新字段，成功后创建**新的** Release，不覆盖已有安装包。

**首次使用前务必备份 Zotero 数据和重要 PDF。** 自动大纲写入可能替换已有目录；请先使用 PDF 副本确认识别、保存、错误处理、插件重启以及进度反馈正常。自动编译成功不等于覆盖所有 Zotero 版本的实机兼容性测试。

## 上游与许可证

原项目：[l0o0/jasminum](https://github.com/l0o0/jasminum)。本项目是独立的非官方衍生版本，非原作者官方发布。保留上游版权，遵循 **AGPL-3.0-or-later**，参见 [LICENSE](LICENSE)。衍生代码可通过固定的上游提交和全部补丁重现。
