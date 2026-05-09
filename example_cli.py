import json
from analysis_skill import BaziAnalysisSkill


def main():
    # 这里用示例数据演示调用方式，实际请替换为你的排盘结果
    bazi_data = {
        "nian": {"tian_gan": {"char": "甲"}, "di_zhi": {"char": "子"}},
        "yue": {"tian_gan": {"char": "丙"}, "di_zhi": {"char": "寅"}},
        "ri": {"tian_gan": {"char": "庚"}, "di_zhi": {"char": "午"}},
        "shi": {"tian_gan": {"char": "壬"}, "di_zhi": {"char": "申"}},
    }
    complete_dayun = [
        {"gan_zhi": "乙丑", "year": 2013, "age": 23},
        {"gan_zhi": "甲子", "year": 2023, "age": 33},
    ]

    skill = BaziAnalysisSkill()
    result = skill.analyze_user_request(
        user_message="帮我分析这个生辰八字",
        bazi_data=bazi_data,
        gender="男",
        complete_dayun=complete_dayun,
        dayun_list=complete_dayun,
    )
    print(json.dumps({"report": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

