# 1. 输入UI原图和渲染的UI图
# 2. GPT对比两张图，输出代码修复建议
# 3. 输入建议和代码，输出修复后代码，截图保存


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import base64
import openai
import time
import argparse
import os
import base64
import openai
import time
from utils.gpt_api import gpt_infer
from utils.refine_prompt import *
import re

refine_suggestion = """
你是一名资深前端工程师，专注于 UI 修复和代码优化。
用户输入一张UI截图，请根据以下规则分析UI截图的问题，并给出修改建议。你的最终输出是修改建议。
规则：
1. 分析布局合理性：组件之间不重叠、对齐方式一致、间距适当。
2. 检查颜色和样式：确保颜色搭配协调、字体大小适中、按钮和输入框样式一致。
3. 内容充实性：确保所有组件都有实际内容，避免空白区域。

请输出修改建议，格式为json对象，包含以下字段：
{
    "layoutIssues": "描述布局问题，如果不存在问题则填None",
    "styleIssues": "描述样式问题，如果不存在问题则填None",
    "contentIssues": "描述内容问题，如果不存在问题则填None"
}
如果没有任何问题，请输出：无
"""

def get_fix_suggestion(image_path):
    try:
        fix_suggestion = gpt_infer(image_path, refine_suggestion)

        # 可选：如果fix_suggestion是字符串形式的JSON，尝试解析成Python对象
        import json
        if fix_suggestion.strip() == "无":
            return "无"
        else:
            return json.loads(fix_suggestion)

    except Exception as e:
        print(f"分析失败: {e}")
        return None