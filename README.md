# bazi-fortuneteller-skill

将“随便算算”网站中的分析能力抽离为可复用的 Python Skill（不包含前端）。

## 包含能力

- 命格分析 Prompt 组装（生辰解读 / 十神格局 / 五行喜忌）
- 大运详情 Prompt 组装
- 对话上下文组装（八字、完整大运、命格分析结果、当前时序信息）
- 用户问题自动分流：泛化分析输出完整报告，具体问题带 `/chat` 上下文回答
- 命格分析结果解析（含结构化五行喜忌提取）
- 通过 DeepSeek(OpenAI SDK 兼容) 调用模型

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python example_cli.py
```

## 主要文件

- `analysis_skill.py`：核心 Skill 类
- `prompt_config.py`：Prompt 模板
- `example_cli.py`：最小调用示例
- `ganzhi.py` / `datas.py` / `bazi_simple.py` 等：从网站后端迁移的命理核心代码

## 推荐调用方式

优先使用 `BaziAnalysisSkill.analyze_user_request()` 处理用户入口：

- 用户只说“帮我分析这个生辰八字”“帮我分析”等，没有限定具体方向时，会生成一份完整报告，包含命格分析、当前三步大运详解、五行喜忌与转运建议。
- 用户问事业、财运、感情、某年运势等具体问题时，会带上 `build_chat_context_string()` 组装的 `/chat` 上下文，只围绕该问题回答。
- `dayun_list` 应由调用侧传入当前三步大运，报告 prompt 直接复用该列表，不会再从完整大运中重新推断。

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

