---
name: bazi-fortuneteller
description: Extracts and runs bazi analysis logic (mingge analysis, dayun detail analysis, and chat context building) without any frontend. Use when the user wants backend-only analysis capability from the suibiansuansuan website.
disable-model-invocation: true
---

# Bazi Fortuneteller Skill

## Instructions

1. Use `BaziAnalysisSkill` from `analysis_skill.py`.
2. User-facing input should provide出生年月日时（`birth_year`, `birth_month`, `birth_day`, `birth_hour`, optional `birth_minute`）and `gender`; the skill computes `bazi_data`, `complete_dayun`, and `dayun_list` internally from existing repo code.
3. If出生年月日时 is missing, `analyze_user_request()` returns a message asking the user to provide it before analysis.
4. For user-facing requests, prefer `analyze_user_request(user_message, ...)`.
5. If the user only asks for a generic analysis such as “帮我分析这个生辰八字” or “帮我分析”, `analyze_user_request()` outputs one full report covering命格分析, 当前三步大运详解, 五行喜忌, and转运建议.
6. If the user asks a concrete question, `analyze_user_request()` answers through the `/chat` context built by `build_chat_context_string()`.
7. Lower-level APIs remain available for callers that already have structured data: for命格分析 call `analyze_mingge()`; for单步大运详情 call `analyze_dayun_detail()`; for对话上下文 call `build_chat_context_string()`.

## Notes

- This skill intentionally excludes any HTML/JS UI logic.
- Model defaults are in `prompt_config.py`.

