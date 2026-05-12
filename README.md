# bazi-fortuneteller-skill

一个用于八字排盘与命理问答的 Python Skill。它面向 agent 或后端调用方：输入用户的出生信息和问题，Skill 负责排盘、生成上下文、调用大模型并返回适合用户阅读的中文回答。

## 能力概览

- 根据出生年月日时、性别自动生成八字、完整大运和当前三步大运。
- 自动计算八字与大运对应的十神、地支藏干十神、神煞。
- 泛化分析请求输出完整报告：命盘详情表、命格分析、当前三步大运、五行喜忌、转运建议。
- 具体问题走 `/chat` 场景：带八字、大运、十神、神煞、命格分析结果等上下文，只回答用户当前问题。
- 时间类问题自动补充时序：目标日期、所属大运、流年、流月、流日干支及对应十神。
- 通过 OpenClaw / OpenAI SDK 兼容接口使用调用环境中的大模型。

## 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 模型配置

运行时优先读取 OpenClaw/OpenAI 兼容环境变量：

- `OPENCLAW_API_KEY` / `OPENCLAW_BASE_URL` / `OPENCLAW_MODEL`
- 兼容 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL`
- 也兼容 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`

如果运行环境没有注入这些变量，可以复制 `.env.example` 后填写本地配置：

```bash
cp .env.example .env
```

不要提交真实 token。`.env` 已被 `.gitignore` 忽略。

## 给 agent 的推荐调用方式

优先使用 `BaziAnalysisSkill.analyze_user_request()` 作为用户入口。

### 1. 用户未提供出生信息

如果用户没有提供出生年月日时，直接调用也可以，Skill 会返回提示用户补充出生信息的文案：

```python
from analysis_skill import BaziAnalysisSkill

skill = BaziAnalysisSkill()
answer = skill.analyze_user_request(user_message="帮我分析一下")
```

返回内容会提示用户提供出生年月日时、性别，以及公历/农历信息。

### 2. 用户要求完整分析报告

用户只说“帮我分析这个生辰八字”“给我分析分析”等，没有限定事业、财运、感情等具体问题时，会走完整报告。

```python
answer = skill.analyze_user_request(
    user_message="我出生时间是1992年8月9日11:50，女，分析一下",
    gender="女",
    birth_year=1992,
    birth_month=8,
    birth_day=9,
    birth_hour=11,
    birth_minute=50,
)
```

完整报告开头会先输出 Markdown 命盘详情表：

- 天干
- 天干十神
- 地支
- 地支藏干十神
- 神煞

随后输出命格分析、当前三步大运详解、五行喜忌和转运建议。

### 3. 用户问具体问题

用户问具体事项时，会走 `/chat` 场景，只围绕问题回答。

```python
answer = skill.analyze_user_request(
    user_message="我今年副业能挣钱吗？",
    gender="女",
    birth_year=1992,
    birth_month=8,
    birth_day=9,
    birth_hour=11,
    birth_minute=50,
)
```

回答会带上内部八字、大运、十神、神煞上下文，但不会把完整报告重新输出给用户。

### 4. 时间类具体问题

如果用户问题涉及时间，例如“明天运势如何”“下个月生孩子会不会顺利”“明年适合跳槽吗”，Skill 会自动计算目标时间的：

- 所属大运
- 流年干支
- 流月干支
- 流日干支
- 对应十神

这些信息会注入模型上下文。最终回答不会机械列出“当前大运/流年/流月/流日”清单，但可以自然引用关键干支或十神解释原因。

```python
answer = skill.analyze_user_request(
    user_message="我下个月生孩子会不会顺利？",
    gender="女",
    birth_year=1992,
    birth_month=8,
    birth_day=9,
    birth_hour=11,
    birth_minute=50,
)
```

## 输入字段

常用字段：

| 字段 | 说明 |
|---|---|
| `user_message` | 用户原始问题 |
| `gender` | 性别，影响大运顺逆 |
| `birth_year` | 出生年 |
| `birth_month` | 出生月 |
| `birth_day` | 出生日 |
| `birth_hour` | 出生小时，24 小时制 |
| `birth_minute` | 出生分钟，默认 `0` |
| `is_lunar` | 是否农历，默认 `False` |
| `leap_month` | 农历是否闰月，默认 `False` |

如果调用方已经有结构化排盘结果，也可以直接传入：

- `bazi_data`
- `complete_dayun`
- `dayun_list`
- `mingge_analysis`

## 主要文件

- `analysis_skill.py`：核心 Skill 类与主要入口。
- `prompt_config.py`：系统提示词和报告模板。
- `example_cli.py`：最小调用示例。
- `bazi_simple.py` / `ganzhi.py` / `datas.py` / `common.py`：排盘、大运、十神、神煞等基础计算。

