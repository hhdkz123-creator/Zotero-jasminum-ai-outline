# 隔离 Zotero 测试

在 macOS 安装 Zotero 10.0.9、Python `reportlab pillow pypdf` 后，从仓库根目录运行：

```sh
python3 tests/native/run_native.py --xpi /absolute/path/to/Zotero-jasminum-ai-outline_v1.1.45-ai.1.xpi
```

测试使用系统 Arial Unicode 字体，生成 297 页中文文字层文档、297 页扫描文档和 17 页完整模式样本。真实启动 Zotero 的独立 `native/profile` 和 `native/data`，通过正式插件工具栏点击入口测试，不读取/修改主 Zotero 配置。测试实例会显示原生窗口，运行后自行退出；最多启动四次以检查缓存与设置重启恢复。

HTTP 请求在该隔离进程中由确定性 fixture 响应，不向真实 AI 服务发出识别请求。模型准确率不属于此测试范围。输出在 `verification/native.json`。重跑前保留并移动既有 `native/` 和 `verification/`，脚本不会静默清空旧结果。
