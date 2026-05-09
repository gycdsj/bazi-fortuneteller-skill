import json
from analysis_skill import BaziAnalysisSkill


def main():
    # 这里用出生信息演示调用方式，Skill 会自动排八字并生成大运。
    skill = BaziAnalysisSkill()
    result = skill.analyze_user_request(
        user_message="帮我分析这个生辰八字",
        gender="男",
        birth_year=1992,
        birth_month=8,
        birth_day=9,
        birth_hour=11,
        birth_minute=50,
    )
    print(json.dumps({"report": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

