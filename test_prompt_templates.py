import unittest

from prompt_config import PROMPT_TEMPLATES
from prompts import build_bazi_analysis_prompt, build_multi_dayun_analysis_prompt


class PromptTemplateRegressionTest(unittest.TestCase):
    def test_required_public_prompt_templates_exist(self):
        self.assertIn("bazi_analysis", PROMPT_TEMPLATES)
        self.assertIn("multi_dayun_analysis", PROMPT_TEMPLATES)

    def test_bazi_analysis_prompt_formats_structured_output_instructions(self):
        prompt = build_bazi_analysis_prompt(
            "年柱：甲子",
            complete_dayun=[{"gan_zhi": "乙丑", "year": 2030, "age": 4}],
        )

        self.assertIn("年柱：甲子", prompt)
        self.assertIn("乙丑（起始年份：2030，对应年龄：4岁）", prompt)
        self.assertIn("1. 生辰解读", prompt)
        self.assertIn("【五行喜忌】", prompt)

    def test_unknown_bazi_analysis_type_falls_back_without_crashing(self):
        prompt = build_bazi_analysis_prompt("年柱：甲子", analysis_type="unknown")

        self.assertIn("年柱：甲子", prompt)
        self.assertIn("1. 生辰解读", prompt)

    def test_multi_dayun_prompt_formats_three_dayuns(self):
        prompt = build_multi_dayun_analysis_prompt("年柱：甲子", ["乙丑", "丙寅", "丁卯"])

        self.assertIn("大运1（乙丑）", prompt)
        self.assertIn("大运2（丙寅）", prompt)
        self.assertIn("大运3（丁卯）", prompt)


if __name__ == "__main__":
    unittest.main()
