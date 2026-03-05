# Project-100X

本次清理后已删除旧的 `KIMI` 文件，仅保留当前可用的项目核心代码：
- `project100x/src/datahub.py`
- `project100x/requirements.txt`

## 本地部署（当前环境）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r project100x/requirements.txt
python project100x/src/datahub.py
```

运行后会下载（或回退生成）示例行情数据并输出结果。

## 将清理后的内容转移到 main（删除 main 旧文件）

如果你当前在功能分支（例如 `work` 或 `codex/...`），可执行：

```bash
git checkout main
git merge --no-ff work
```

如果远端存在 `main`，再推送：

```bash
git push origin main
```

这样 `main` 就会同步当前分支上的清理结果（包括删除旧文件 `KIMI`）。
