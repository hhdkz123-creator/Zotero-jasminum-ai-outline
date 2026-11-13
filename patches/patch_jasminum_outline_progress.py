#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为已安装「静默 AI 大纲」补丁的 Jasminum v1.1.44 源码添加非弹窗进度反馈。

用法：python3 /path/to/patch_jasminum_outline_progress.py .
运行目录为 Jasminum 源码根目录。脚本会保留 *.progress-feedback.bak 备份。
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path.cwd()
view_file = root / "src/modules/outline/taskView.ts"
index_file = root / "src/modules/outline/index.ts"
for f in (view_file, index_file):
    if not f.is_file():
        raise SystemExit(f"错误：缺少源码文件 {f}")

view = view_file.read_text(encoding="utf-8")
index = index_file.read_text(encoding="utf-8")
marker = "export type OutlineAIProgress = {"
if marker in view and "j-outline-ai-progress" in index:
    print("进度反馈补丁已存在，无须重复修改。")
    raise SystemExit(0)
if marker in view or "j-outline-ai-progress" in index:
    raise SystemExit("检测到只有部分文件包含进度补丁。请勿重复覆盖，请先检查源代码。")

start = view.find("export async function openOutlineTask(item: Zotero.Item) {")
end = view.find("\nexport function addOutlineControls(", start)
if start < 0 or end < 0 or "后台静默识别" not in view[start:end]:
    raise SystemExit("错误：未检测到此前的静默识别补丁，停止修改（本脚本不适用于原版）。")
if view.count("export async function openOutlineTask(item: Zotero.Item) {") != 1:
    raise SystemExit("错误：识别入口不唯一，停止修改。")

old_click = '''  toolbar
    .querySelector("#j-outline-ai")
    ?.addEventListener("click", () => openOutlineTask(reader._item));'''
if index.count(old_click) != 1 or 'for (const id of ["j-outline-save-pdf"]) {' not in index:
    raise SystemExit("错误：工具栏代码与已修改版本不一致，停止修改。")

new_view = '''export type OutlineAIProgress = {
  phase: "preparing" | "recognizing" | "saving";
  completed: number;
  total: number;
};

export async function openOutlineTask(
  item: Zotero.Item,
  onProgress?: (progress: OutlineAIProgress) => void,
) {
  // 保留静默识别 + 自动保存，仅增加进度订阅，不创建进度/校对窗口。
  onProgress?.({ phase: "preparing", completed: 0, total: 0 });
  const attachment = item.isPDFAttachment()
    ? item
    : item.isRegularItem()
      ? (await item.getBestAttachments()).find(
          (a) => a.isPDFAttachment() && !a.deleted,
        )
      : undefined;
  const target = attachment ?? item;
  const existing = addon.taskRunner.getTaskById(`outline-${target.id}`);
  if (
    existing instanceof OutlineTask &&
    (["waiting", "processing"].includes(existing.status) || existing.saving)
  ) return;

  const removeTask = (task: OutlineTask) => {
    const index = addon.taskRunner.tasks.indexOf(task);
    if (index >= 0) addon.taskRunner.tasks.splice(index, 1);
  };

  let unsubscribe: (() => void) | undefined;
  const watchProgress = (task: OutlineTask) => {
    unsubscribe?.();
    const update = () => {
      onProgress?.({
        phase: task.saving
          ? "saving"
          : task.status === "waiting"
            ? "preparing"
            : "recognizing",
        completed: task.completedPages,
        total: task.totalPages,
      });
    };
    unsubscribe = task.subscribe(update);
    update();
  };

  try {
    let task: OutlineTask;
    if (existing instanceof OutlineTask && existing.canApply) {
      // 保存失败时重试写入，避免再次调用收费接口。
      task = existing;
      watchProgress(task);
    } else if (existing instanceof OutlineTask && existing.canResume) {
      // 保留先前的页面识别进度。
      task = existing;
      watchProgress(task);
      await addon.taskRunner.retryOutlineTask(task);
    } else {
      if (existing instanceof OutlineTask) removeTask(existing);
      task = new OutlineTask(target);
      watchProgress(task);
      await addon.taskRunner.addTask(task);
    }

    if (task.canApply) {
      onProgress?.({
        phase: "saving",
        completed: task.completedPages,
        total: task.totalPages,
      });
      await task.apply(); // 同时更新 PDF 和茉莉花大纲，并刷新阅读器。
      if (task.applied) {
        removeTask(task);
        return; // 成功后自动恢复按钮，不显示通知。
      }
    }
    throw new Error(
      [task.summary, task.message].filter(Boolean).join("\\n") ||
        "识别未产生有效大纲",
    );
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    ztoolkit.log("后台 AI 大纲识别或自动保存失败", error);
    const reader = Zotero.Reader._readers.find(
      (entry) => entry._item.id === target.id,
    );
    (reader?._iframeWindow ?? Zotero.getMainWindow()).alert(
      `AI 全文大纲识别失败\\n\\n${detail}\\n\\n请检查错误原因，然后再次点击工具栏按钮重试。`,
    );
  } finally {
    unsubscribe?.();
  }
}
'''

new_click = '''  // 非模态状态反馈：旋转图标 + 本页数进度；识别成功时自动还原。
  const aiButton = toolbar.querySelector<HTMLButtonElement>("#j-outline-ai");
  if (aiButton) {
    const status = doc.createElement("span");
    status.className = "j-outline-ai-progress";
    status.hidden = true;
    status.setAttribute("aria-live", "off");
    aiButton.insertAdjacentElement("afterend", status);

    if (!doc.getElementById("j-outline-ai-progress-style")) {
      const style = doc.createElement("style");
      style.id = "j-outline-ai-progress-style";
      style.textContent = `
        @keyframes jasminum-ai-spin { to { transform: rotate(360deg); } }
        #j-outline-toolbar #j-outline-ai.j-outline-ai-busy svg {
          animation: jasminum-ai-spin 1.1s linear infinite;
        }
        #j-outline-toolbar .j-outline-ai-progress:not([hidden]) {
          display: inline-block;
          flex: 0 1 78px;
          min-width: 0;
          max-width: 78px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          font-size: 11px;
          color: var(--accent-blue, #2675ba);
        }
        #j-outline-toolbar #j-outline-ai.j-outline-ai-busy {
          color: var(--accent-blue, #2675ba);
          cursor: progress;
        }
      `;
      doc.head.append(style);
    }

    const iconHTML = aiButton.innerHTML;
    const defaultTitle = aiButton.title;
    let working = false;
    const show = (label: string, details: string) => {
      if (!aiButton.isConnected) return;
      status.hidden = false;
      status.textContent = label;
      status.title = details;
      aiButton.title = details;
      aiButton.setAttribute("aria-label", details);
    };
    aiButton.addEventListener("click", async () => {
      if (working) return;
      working = true;
      aiButton.disabled = true;
      aiButton.classList.add("j-outline-ai-busy");
      aiButton.setAttribute("aria-busy", "true");
      aiButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" aria-hidden="true">
        <path d="M21 12a9 9 0 1 1-9-9"/></svg>`;
      show("准备中", "AI 大纲识别：正在准备 PDF 页面");
      try {
        await openOutlineTask(reader._item, (progress) => {
          if (progress.phase === "saving") {
            show("写入中", "识别完成，正在自动保存 PDF 大纲");
          } else if (progress.phase === "preparing") {
            show("准备中", "正在准备或等待开始 AI 大纲识别");
          } else if (progress.total > 0) {
            show(
              `${progress.completed}/${progress.total} 页`,
              `AI 大纲识别中：${progress.completed}/${progress.total} 页`,
            );
          } else {
            show("识别中", "正在使用 AI 识别全文大纲");
          }
        });
      } finally {
        working = false;
        aiButton.disabled = false;
        aiButton.classList.remove("j-outline-ai-busy");
        aiButton.removeAttribute("aria-busy");
        aiButton.innerHTML = iconHTML;
        aiButton.title = defaultTitle;
        aiButton.setAttribute("aria-label", defaultTitle);
        status.hidden = true;
        status.textContent = "";
      }
    });
  }'''

new_index = index.replace(old_click, new_click, 1)
new_view_text = view[:start] + new_view + view[end:]

for f, original in ((view_file, view), (index_file, index)):
    backup = f.with_suffix(f.suffix + ".progress-feedback.bak")
    if backup.exists():
        raise SystemExit(f"备份文件已存在，避免覆盖：{backup}")
    backup.write_text(original, encoding="utf-8")
view_file.write_text(new_view_text, encoding="utf-8")
index_file.write_text(new_index, encoding="utf-8")
print("成功：已添加运行中旋转图标、识别页数、保存状态，并保留静默成功/失败弹窗行为。")
print("已备份：taskView.ts.progress-feedback.bak、index.ts.progress-feedback.bak")
print("下一步：npx -y pnpm@9.15.1 run build")
