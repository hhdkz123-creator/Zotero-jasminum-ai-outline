# Jasminum AI 大纲优化版

基于 [茉莉花（Jasminum）](https://github.com/l0o0/jasminum) **1.1.44** 的定制版本，优化 Zotero PDF 阅读器的「AI 全文大纲识别」流程。

> 本仓库包含**增量修改脚本与自动构建工作流**，而非直接复制的完整上游源码。构建时固定检出上游提交 `9af49f7175d2257a15d1ee1598da893569510e29`，应用本仓库补丁并打包 XPI。

## 功能

- **静默运行**：点击大纲工具栏中的 AI 图标后，在后台识别，不弹出遮挡 PDF 的任务或校对窗口。
- **自动保存**：识别完成后自动调用上游已有的保存逻辑，写入 PDF 和茉莉花大纲，刷新阅读器。
- **图标常驻**：AI 全文大纲识别按钮直接显示在大纲工具栏，不必展开「⋮」。
- **过程反馈**：识别时 AI 图标旋转，并显示已完成页数；写入时显示「写入中」；成功后恢复原状。
- **失败提示**：识别或写入失败时弹出错误信息；重试时尽量复用已经成功识别的页面。

## 安装

在 [Releases](https://github.com/hhdkz123-creator/jasminum-ai-outline/releases) 下载 `.xpi` 文件，打开 Zotero → 工具 → 插件 → 齿轮 → 从文件安装插件，安装后重启 Zotero。若已有原版茉莉花，先备份数据并确认插件兼容性。

打开 PDF → 左侧茉莉花大纲 → 点击星光 AI 图标。首次使用需先到 Zotero 设置中的茉莉花「AI 识别」配置兼容多模态输入的 API 和模型。**本仓库不包含也不需要你的 API Key。**

## 构建

构建由 [GitHub Actions](.github/workflows/build-release.yml) 自动执行，无需本地配置：

1. 固定下载上游 `l0o0/jasminum` 的指定提交。
2. 运行 [静默识别补丁](patches/patch_jasminum_silent_outline.py)，随后运行 [进度反馈补丁](patches/patch_jasminum_outline_progress.py)。
3. 使用 Node.js 22 + pnpm 9.15.1 安装依赖并运行 `pnpm run build`。
4. 将构建出的 XPI 作为 Actions Artifact 上传，并在成功后发布到 Releases（若仓库 Actions 权限允许）。

## 注意事项

- **请先使用 PDF 副本测试。** 自动保存可能替换原有大纲；识别时对 PDF 人工大纲的修改会触发冲突检测，但这不等于对所有已有人工内容提供无损合并。
- 识别按上游实现发送 PDF 页面图片给已配置的 AI 服务，相关 API 调用可能产生费用。
- 自动化构建成功不等于在所有 Zotero 环境中实机验证。建议先验证识别、保存、错误处理及插件重启。
- 定制版与原版可能使用相同插件 ID；官方插件自动更新可能覆盖修改。

## 上游与许可证

原项目：[l0o0/jasminum](https://github.com/l0o0/jasminum)，原作者及贡献者拥有相应版权。此项目是非官方衍生修改版，与上游无官方关联。

依据上游许可证，以 **GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)** 发布；参见 [LICENSE](LICENSE)。对上游源码的改动由本仓库补丁记录。
