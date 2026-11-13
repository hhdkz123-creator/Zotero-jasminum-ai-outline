#!/usr/bin/env python3
"""Patch l0o0/jasminum v1.1.44 sources for silent AI outline generation.

Run from the repository root or pass the root as an argument.
Always back up originals before modifying and rebuild/test in Zotero.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

def patch(rel, old, new):
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"缺少源码文件：{path}")
    original = path.read_text(encoding="utf-8")
    if new in original:
        print(f"跳过（已修改）：{rel}")
        return
    if original.count(old) != 1:
        raise SystemExit(f"源码版本不匹配，请勿强行覆盖：{rel}（匹配 {original.count(old)} 次）")
    backup = path.with_suffix(path.suffix + ".silent-outline.bak")
    if not backup.exists():
        backup.write_text(original, encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    print(f"已修改：{rel}（备份：{backup.name}）")

patch(
    "src/modules/outline/task.ts",
    "  readonly silent = false;",
    "  readonly silent = true;",
)

view = root / "src/modules/outline/taskView.ts"
if not view.is_file():
    raise SystemExit("缺少源码文件：src/modules/outline/taskView.ts")
s = view.read_text(encoding="utf-8")
start = s.find("export async function openOutlineTask(item: Zotero.Item) {")
end = s.find("\nexport function addOutlineControls(", start)
if start < 0 or end < 0:
    if "async function openOutlineTask(item: Zotero.Item)" in s and "后台静默识别" in s:
        print("跳过（已修改）：src/modules/outline/taskView.ts")
    else:
        raise SystemExit("taskView.ts 结构和 v1.1.44 不一致，已停止修改")
else:
    replacement = '''export async function openOutlineTask(item: Zotero.Item) {
  // 后台静默识别：不打开进度窗口、也不打开大纲核对弹窗。
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

  try {
    let task: OutlineTask;
    if (existing instanceof OutlineTask && existing.canApply) {
      // 保存失败时直接重试写入，避免重新调用付费 API。
      task = existing;
    } else if (existing instanceof OutlineTask && existing.canResume) {
      // 保留之前的页面识别进度。
      task = existing;
      await addon.taskRunner.retryOutlineTask(task);
    } else {
      if (existing instanceof OutlineTask) removeTask(existing);
      task = new OutlineTask(target);
      await addon.taskRunner.addTask(task);
    }

    if (task.canApply) {
      await task.apply(); // 已有逻辑：同时写入 PDF 和茉莉花本地大纲，并刷新阅读器。
      if (task.applied) {
        removeTask(task);
        return; // 成功后完全静默。
      }
    }
    throw new Error([task.summary, task.message].filter(Boolean).join("\\n") || "识别未产生有效大纲");
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    ztoolkit.log("后台 AI 大纲识别或自动保存失败", error);
    const reader = Zotero.Reader._readers.find(
      (entry) => entry._item.id === target.id,
    );
    (reader?._iframeWindow ?? Zotero.getMainWindow()).alert(
      `AI 全文大纲识别失败\\n\\n${detail}\\n\\n请检查错误原因，然后再次点击工具栏按钮重试。`,
    );
  }
}
'''
    original = s
    backup = view.with_suffix(view.suffix + ".silent-outline.bak")
    if not backup.exists():
        backup.write_text(s, encoding="utf-8")
    view.write_text(s[:start] + replacement + s[end:], encoding="utf-8")
    print(f"已修改：src/modules/outline/taskView.ts（备份：{backup.name}）")

patch(
    "src/modules/outline/index.ts",
    'for (const id of ["j-outline-ai", "j-outline-save-pdf"]) {',
    'for (const id of ["j-outline-save-pdf"]) {',
)

print("\n修改完成。此脚本不会修改已安装的 Zotero 插件；需要依照原仓库步骤重新编译 XPI 并安装。")
