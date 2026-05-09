import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

from prompt_config import CHAT_SYSTEM_PROMPT, DEEPSEEK_CONFIG, PROMPT_TEMPLATES, SYSTEM_PROMPTS


class BaziAnalysisSkill:
    GENERAL_ANALYSIS_ACTIONS = ("分析", "看看", "看下", "看一下", "解读", "算算", "测测")
    GENERAL_ANALYSIS_SUBJECTS = ("八字", "生辰", "命盘", "命格", "排盘")
    SPECIFIC_QUESTION_KEYWORDS = (
        "事业",
        "工作",
        "财运",
        "财富",
        "赚钱",
        "感情",
        "婚姻",
        "桃花",
        "健康",
        "学业",
        "考试",
        "子女",
        "父母",
        "买房",
        "投资",
        "创业",
        "跳槽",
        "离职",
        "复合",
        "离婚",
        "今年",
        "明年",
        "哪年",
        "什么时候",
        "大运",
        "流年",
        "适合",
        "能不能",
        "会不会",
        "要不要",
        "怎么",
        "如何",
        "为什么",
    )

    def __init__(self, api_key=None, base_url=None, model=None):
        load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model or os.getenv("DEEPSEEK_MODEL", DEEPSEEK_CONFIG["model"])
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    @staticmethod
    def build_bazi_info_string(bazi_data, gender):
        return (
            "八字信息：\n"
            f"年柱：{bazi_data['nian']['tian_gan']['char']}{bazi_data['nian']['di_zhi']['char']}\n"
            f"月柱：{bazi_data['yue']['tian_gan']['char']}{bazi_data['yue']['di_zhi']['char']}\n"
            f"日柱：{bazi_data['ri']['tian_gan']['char']}{bazi_data['ri']['di_zhi']['char']}\n"
            f"时柱：{bazi_data['shi']['tian_gan']['char']}{bazi_data['shi']['di_zhi']['char']}\n"
            f"性别：{gender}\n"
            f"日主：{bazi_data['ri']['tian_gan']['char']}"
        )

    @staticmethod
    def format_complete_dayun(complete_dayun):
        if not complete_dayun:
            return "未提供完整大运信息。"
        lines = []
        for i, yun in enumerate(complete_dayun, start=1):
            gan_zhi = BaziAnalysisSkill._format_ganzhi(
                BaziAnalysisSkill._get_dayun_value(yun, "gan_zhi", "ganzhi")
            )
            year = BaziAnalysisSkill._get_dayun_value(yun, "year", "start_year")
            age = BaziAnalysisSkill._get_dayun_value(yun, "age", "start_age")
            lines.append(
                f"{i}. {gan_zhi}（起始年份：{year}，对应年龄：{age}岁）"
            )
        return "\n".join(lines)

    @staticmethod
    def _get_dayun_value(dayun, *names):
        for name in names:
            if isinstance(dayun, dict) and name in dayun:
                return dayun.get(name, "")
            if hasattr(dayun, name):
                return getattr(dayun, name)
        return ""

    @staticmethod
    def _format_ganzhi(value):
        if isinstance(value, (list, tuple)):
            return "".join(str(item) for item in value)
        return "" if value is None else str(value)

    @classmethod
    def is_default_report_request(cls, user_message):
        """判断用户是否只是在泛化地要求分析八字，而非追问具体事项。"""
        normalized = (user_message or "").strip().replace(" ", "")
        if not normalized:
            return True

        has_action = any(keyword in normalized for keyword in cls.GENERAL_ANALYSIS_ACTIONS)
        has_subject = any(keyword in normalized for keyword in cls.GENERAL_ANALYSIS_SUBJECTS)
        if not has_action:
            return False

        if any(keyword in normalized for keyword in cls.SPECIFIC_QUESTION_KEYWORDS):
            return False

        return has_subject or len(normalized) <= 8

    @classmethod
    def format_dayun_window(cls, dayun_list):
        if not dayun_list:
            return "未提供当前三步大运信息。"
        lines = []
        for i, dayun in enumerate(dayun_list, start=1):
            gan_zhi = cls._format_ganzhi(cls._get_dayun_value(dayun, "gan_zhi", "ganzhi"))
            year = cls._get_dayun_value(dayun, "year", "start_year")
            age = cls._get_dayun_value(dayun, "age", "start_age")
            lines.append(f"{i}. {gan_zhi}（起始年份：{year}，对应年龄：{age}岁）")
        return "\n".join(lines)

    @staticmethod
    def format_mingge_analysis(mingge_analysis):
        if not mingge_analysis:
            return "未提供。"

        if isinstance(mingge_analysis, str):
            return mingge_analysis

        lines = []
        if mingge_analysis.get("shengchen"):
            lines.append(f"生辰解读：{mingge_analysis['shengchen']}")
        if mingge_analysis.get("shishen"):
            lines.append(f"十神格局：{mingge_analysis['shishen']}")
        if mingge_analysis.get("xiji"):
            lines.append(f"五行喜忌：{mingge_analysis['xiji']}")
        if mingge_analysis.get("element_like"):
            lines.append("喜用五行：" + "、".join(mingge_analysis["element_like"]))
        if mingge_analysis.get("element_dislike"):
            lines.append("忌讳五行：" + "、".join(mingge_analysis["element_dislike"]))
        return "\n".join(lines) if lines else "未提供。"

    @staticmethod
    def build_current_time_context():
        now = datetime.now()
        return (
            "当前时序信息：\n"
            f"当前公历日期：{now:%Y-%m-%d}\n"
            "本月干支：请由调用侧传入或在业务层补充\n"
            "今日干支：请由调用侧传入或在业务层补充"
        )

    def build_chat_context_string(
        self,
        bazi_data,
        gender,
        da_yun=None,
        complete_dayun=None,
        mingge_analysis=None,
        current_month_ganzhi=None,
        current_day_ganzhi=None,
    ):
        parts = [self.build_bazi_info_string(bazi_data, gender)]
        parts.append(
            "当前时序信息：\n"
            f"当前公历日期：{datetime.now():%Y-%m-%d}\n"
            f"本月干支：{current_month_ganzhi or '未提供'}\n"
            f"今日干支：{current_day_ganzhi or '未提供'}"
        )
        if complete_dayun:
            parts.append("完整大运（10步）：\n" + self.format_complete_dayun(complete_dayun))
        if da_yun:
            lines = ["当前展示大运："]
            for y in da_yun:
                year = self._get_dayun_value(y, "year", "start_year")
                gan_zhi = self._format_ganzhi(self._get_dayun_value(y, "gan_zhi", "ganzhi"))
                lines.append(f"- {year}年 {gan_zhi}")
            parts.append("\n".join(lines))
        if mingge_analysis:
            parts.append("命格分析结果：\n" + self.format_mingge_analysis(mingge_analysis))
        return "\n\n".join(parts)

    def _chat(self, system_prompt, user_prompt, temperature=None):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=DEEPSEEK_CONFIG["temperature"] if temperature is None else temperature,
            stream=False,
            timeout=DEEPSEEK_CONFIG["timeout"],
        )
        return response.choices[0].message.content or ""

    def build_bazi_analysis_prompt(self, bazi_info, complete_dayun=None):
        return PROMPT_TEMPLATES["bazi_analysis"].format(
            bazi_info=bazi_info,
            complete_dayun=self.format_complete_dayun(complete_dayun),
        )

    def build_dayun_analysis_prompt(self, bazi_info, dayun_ganzhi, complete_dayun=None):
        return PROMPT_TEMPLATES["dayun_analysis"].format(
            bazi_info=bazi_info,
            dayun_ganzhi=dayun_ganzhi,
            complete_dayun=self.format_complete_dayun(complete_dayun),
        )

    def build_default_report_prompt(
        self,
        bazi_info,
        complete_dayun=None,
        dayun_list=None,
        mingge_analysis=None,
    ):
        return PROMPT_TEMPLATES["default_report"].format(
            bazi_info=bazi_info,
            complete_dayun=self.format_complete_dayun(complete_dayun),
            dayun_list=self.format_dayun_window(dayun_list),
            existing_mingge_analysis=self.format_mingge_analysis(mingge_analysis),
        )

    def parse_ai_analysis(self, content):
        analysis = {"shengchen": "", "shishen": "", "xiji": "", "element_like": [], "element_dislike": []}
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        section = None
        buf = []

        def flush():
            if section and buf:
                analysis[section] = " ".join(buf).strip()

        for line in lines:
            if "1. 生辰解读" in line:
                flush()
                section = "shengchen"
                buf = [line.split("：", 1)[-1].strip()] if "：" in line else []
                continue
            if "2. 十神格局" in line:
                flush()
                section = "shishen"
                buf = [line.split("：", 1)[-1].strip()] if "：" in line else []
                continue
            if "3. 五行喜忌" in line:
                flush()
                section = "xiji"
                buf = [line.split("：", 1)[-1].strip()] if "：" in line else []
                continue
            if "【五行喜忌】" in line:
                flush()
                section = None
                buf = []
                continue
            if line.startswith("喜用五行："):
                for c in line:
                    if c in ["金", "木", "水", "火", "土"]:
                        analysis["element_like"].append(c)
                continue
            if line.startswith("忌讳五行："):
                for c in line:
                    if c in ["金", "木", "水", "火", "土"]:
                        analysis["element_dislike"].append(c)
                continue
            if section:
                buf.append(line)
        flush()
        analysis["element_like"] = sorted(set(analysis["element_like"]))
        analysis["element_dislike"] = sorted(set(analysis["element_dislike"]))
        return analysis

    def analyze_mingge(self, bazi_data, gender, complete_dayun=None):
        bazi_info = self.build_bazi_info_string(bazi_data, gender)
        prompt = self.build_bazi_analysis_prompt(bazi_info, complete_dayun=complete_dayun)
        content = self._chat(SYSTEM_PROMPTS["bazi_analysis"], prompt)
        return self.parse_ai_analysis(content)

    def analyze_dayun_detail(self, bazi_data, gan_zhi, gender="男", complete_dayun=None):
        bazi_info = self.build_bazi_info_string(bazi_data, gender)
        prompt = self.build_dayun_analysis_prompt(bazi_info, gan_zhi, complete_dayun=complete_dayun)
        content = self._chat(SYSTEM_PROMPTS["bazi_analysis"], prompt)
        return content

    def analyze_default_report(
        self,
        bazi_data,
        gender,
        complete_dayun=None,
        dayun_list=None,
        da_yun=None,
        mingge_analysis=None,
    ):
        bazi_info = self.build_bazi_info_string(bazi_data, gender)
        report_dayun_list = dayun_list if dayun_list is not None else da_yun
        prompt = self.build_default_report_prompt(
            bazi_info,
            complete_dayun=complete_dayun,
            dayun_list=report_dayun_list,
            mingge_analysis=mingge_analysis,
        )
        return self._chat(SYSTEM_PROMPTS["default_report"], prompt)

    def answer_chat_question(
        self,
        user_message,
        bazi_data,
        gender,
        da_yun=None,
        complete_dayun=None,
        mingge_analysis=None,
        current_month_ganzhi=None,
        current_day_ganzhi=None,
    ):
        context = self.build_chat_context_string(
            bazi_data=bazi_data,
            gender=gender,
            da_yun=da_yun,
            complete_dayun=complete_dayun,
            mingge_analysis=mingge_analysis,
            current_month_ganzhi=current_month_ganzhi,
            current_day_ganzhi=current_day_ganzhi,
        )
        prompt = (
            f"{context}\n\n"
            f"用户问题：{user_message}\n\n"
            "请结合以上 /chat 上下文回答用户的具体问题。只围绕问题本身分析，"
            "不要重新输出完整命格报告。"
        )
        return self._chat(CHAT_SYSTEM_PROMPT, prompt)

    def analyze_user_request(
        self,
        user_message,
        bazi_data,
        gender,
        dayun_list=None,
        da_yun=None,
        complete_dayun=None,
        mingge_analysis=None,
        current_month_ganzhi=None,
        current_day_ganzhi=None,
    ):
        active_dayun_list = dayun_list if dayun_list is not None else da_yun
        if self.is_default_report_request(user_message):
            return self.analyze_default_report(
                bazi_data=bazi_data,
                gender=gender,
                complete_dayun=complete_dayun,
                dayun_list=active_dayun_list,
                mingge_analysis=mingge_analysis,
            )

        return self.answer_chat_question(
            user_message=user_message,
            bazi_data=bazi_data,
            gender=gender,
            da_yun=active_dayun_list,
            complete_dayun=complete_dayun,
            mingge_analysis=mingge_analysis,
            current_month_ganzhi=current_month_ganzhi,
            current_day_ganzhi=current_day_ganzhi,
        )

