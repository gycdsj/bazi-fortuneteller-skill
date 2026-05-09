# bazi-fortuneteller-skill

将“随便算算”网站中的分析能力抽离为可复用的 Python Skill（不包含前端）。

## 包含能力

- 命格分析 Prompt 组装（生辰解读 / 十神格局 / 五行喜忌）
- 大运详情 Prompt 组装
- 对话上下文组装（八字、完整大运、命格分析结果、当前时序信息）
- 根据用户提供的出生年月日时自动排八字并生成大运
- 用户问题自动分流：泛化分析输出完整报告，具体问题带 `/chat` 上下文回答
- 命格分析结果解析（含结构化五行喜忌提取）
- 通过 OpenClaw / OpenAI SDK 兼容接口调用用户运行环境中的大模型

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如果运行环境已经注入 OpenClaw/OpenAI 兼容变量，可直接运行示例；否则先复制 `.env.example` 为 `.env` 并填写本地变量：

```bash
# 运行环境已注入模型变量时
python example_cli.py

# 运行环境未注入模型变量时，先复制并填写 .env
cp .env.example .env

# 配置完成后运行示例
python example_cli.py
```

`.env` 中不要写入或提交真实 token。运行时优先读取调用环境提供的 OpenClaw/OpenAI 兼容变量：

- `OPENCLAW_API_KEY` / `OPENCLAW_BASE_URL` / `OPENCLAW_MODEL`
- 兼容 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL`
- 也可在初始化 `BaziAnalysisSkill` 时传入 `client`、`api_key`、`base_url`、`model`

## 主要文件

- `analysis_skill.py`：核心 Skill 类
- `prompt_config.py`：Prompt 模板
- `example_cli.py`：最小调用示例
- `ganzhi.py` / `datas.py` / `bazi_simple.py` 等：从网站后端迁移的命理核心代码

## 推荐调用方式

优先使用 `BaziAnalysisSkill.analyze_user_request()` 处理用户入口：

- 用户提供出生年月日时后，Skill 会通过仓库内排盘代码自动生成 `bazi_data`、`complete_dayun` 和 `dayun_list`。
- 如果用户没有提供出生年月日时，会先提示用户补充出生年月日时，再进行分析。
- 用户只说“帮我分析这个生辰八字”“帮我分析”等，没有限定具体方向时，会生成一份完整报告，包含命格分析、当前三步大运详解、五行喜忌与转运建议。
- 用户问事业、财运、感情、某年运势等具体问题时，会带上 `build_chat_context_string()` 组装的 `/chat` 上下文，只围绕该问题回答。
- 调用侧已经有结构化排盘结果时，也可以继续直接传入 `bazi_data`、`complete_dayun` 和 `dayun_list`。

## 与私有网页仓同步

本仓库用于开源 skill，网页仓保持私有。推荐通过同步脚本保持两边核心代码一致：

- 从私有网页仓同步到 skill 仓：
  - `./scripts/sync_from_web.sh`
- 从 skill 仓回写到私有网页仓：
  - `./scripts/sync_to_web.sh`

脚本默认网页仓路径为：

- `../suibiansuansuan`

如果你的路径不同，可先设置环境变量：

```bash
WEB_REPO_DIR=/your/private/web/repo ./scripts/sync_from_web.sh
```

