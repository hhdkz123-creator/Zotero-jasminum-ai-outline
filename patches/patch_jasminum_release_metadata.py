#!/usr/bin/env python3
"""Brand a pinned Jasminum source checkout as Zotero-jasminum-ai-outline.

Package version is valid semver (1.1.44-ai.2), whereas Firefox/Zotero
manifest version is numeric (1.1.44.2), newer than upstream 1.1.44.
The original add-on ID is retained to make this a replacement rather than
a second conflicting installation. Disable the upstream auto-update URL.
"""
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
pkg_path = root / "package.json"
manifest_path = root / "addon" / "manifest.json"
config_path = root / "zotero-plugin.config.ts"

pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
if pkg.get("version") != "1.1.44":
    raise SystemExit("仅支持固定的上游版本 1.1.44")
if pkg["config"]["addonID"] != "jasminum@linxzh.com":
    raise SystemExit("插件 ID 与预期不符，已终止")
pkg["version"] = "1.1.44-ai.2"
pkg["config"]["addonName"] = "Zotero-jasminum-ai-outline"
pkg["description"] = "Zotero Jasminum AI outline enhanced edition (unofficial)"
pkg["homepage"] = "https://github.com/hhdkz123-creator/jasminum-ai-outline"
pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
zotero = manifest["applications"]["zotero"]
if zotero.get("id") != "__addonID__":
    raise SystemExit("未找到预期的 manifest 插件 ID 模板")
zotero.pop("update_url", None)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

config = config_path.read_text(encoding="utf-8")
needle = "buildVersion: pkg.version,"
if config.count(needle) != 1:
    raise SystemExit("找不到唯一的 buildVersion 配置")
config_path.write_text(
    config.replace(needle, 'buildVersion: "1.1.44.2",', 1),
    encoding="utf-8",
)
print("版本与名称已更新；已移除上游自动更新地址，保留原插件 ID。")
