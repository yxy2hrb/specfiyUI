import os
import json
import base64
import re
import time
from app import BACKEND_RESULTS
from utils.gpt_api import gpt_infer, gpt_infer_no_image
from utils.prompt import *
from utils.spec_prompt import *
from spec_editor import edit_ui_spec_v2
from code_gen.gen_code import gen_code_with_spec
from code_gen.code_debug import iterative_debug

"""
import os
from openai import OpenAI


client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"},
    ],
    # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
    # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
    # extra_body={"enable_thinking": False},
)
print(completion.model_dump_json())
"""
DEST_FOLDER = "/media/sda5/cyn-workspace/UI-SPEC/backend_results/image-results/gen_code_result"
CODE_PATH = "/media/sda5/cyn-workspace/UI-SPEC/my-app/src/App.js"
CODE_DIR = "/media/sda5/cyn-workspace/UI-SPEC/my-app"
SCRIPT_PATH = "/media/sda5/cyn-workspace/UI-SPEC/my-app/src/transform-recharts-animation.js"
PORT = 41000
WAIT_SELECTOR = "#root"

def extract_json_block(text):
    """
    使用正则从文本中提取第一个 JSON 对象
    """
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if matches:
        return matches[0]
    return text  # 如果没匹配到，就原样返回（可能本来就是 JSON）

def parse_json_with_retries(text, retries=4, wait=0.5):
    for i in range(retries):
        try:
            extracted = extract_json_block(text)
            return json.loads(extracted)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error {i+1}/{retries}: {e}")
            time.sleep(wait)
    return text

def decode_image(b64_string):
    try:
        if b64_string.startswith("data:image"):
            b64_string = re.sub("^data:image/.+;base64,", "", b64_string)
        return base64.b64decode(b64_string)
    except Exception as e:
        raise ValueError(f"Base64 解码错误: {e}")

def image_to_spec(img_bytes, save_path):
    with open(save_path, "wb") as f:
        f.write(img_bytes)
    # result = gpt_infer(save_path, page_prompt_cwk)
    result = gpt_infer(save_path, overall_design_spec_prompt_cn)
    return parse_json_with_retries(result)

# def adjust_spec_layout(spec):
#     prompt_text = adjust_layout_by_bbox_prompt.format(spec_input=json.dumps(spec, ensure_ascii=False, indent=2))
#     result = gpt_infer_no_image(prompt_text)
#     return parse_json_with_retries(result)

def text_to_spec(text):
    result = gpt_infer_no_image(text_to_spec_prompt.format(text=text))
    return parse_json_with_retries(result)

def edit_spec(text, spec, output_name):
    return edit_ui_spec_v2(text, spec, f"{output_name}-edit.json")

# def combine_specs(spec_list):
#     prompt = merge_prompt.format(spec_list=",".join(spec_list))
#     return parse_json_with_retries(gpt_infer_no_image(prompt))

def generate_spec_from_intent(user_input: str):
    """
    基于用户的设计意图自然语言描述，生成结构化 UI 规范 SPEC。
    """
    prompt = intent_to_spec_prompt.format(user_input=user_input)
    result_text = gpt_infer_no_image(prompt)
    return parse_json_with_retries(result_text)

def generate_code(spec, save_name):
    code = gen_code_with_spec(save_name, spec, DEST_FOLDER, code_prompt_web_v9)

    with open(CODE_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    screenshot_path = os.path.join(DEST_FOLDER, f"{save_name}_screenshot.png")
    success = iterative_debug(code_path=CODE_PATH, port=PORT, code_dir=CODE_DIR, script_path=SCRIPT_PATH, wait_selector=WAIT_SELECTOR, screenshot=screenshot_path)
    if success:
        with open(screenshot_path, "rb") as img:
            return code, base64.b64encode(img.read()).decode("utf-8")
        # attempt += 1
    return None, None

def analyze_image_reference(img_b64: str, spec: dict, save_name: str):
    """
    接收 base64 图像和 spec，返回图像属性 JSON 并保存为文件
    """
    try:
        img_bytes = decode_image(img_b64)
    except Exception as e:
        raise ValueError(f"Base64 解码失败: {e}")
    save_path = os.path.join(BACKEND_RESULTS, f"{save_name}.png")
    
    with open(save_path, "wb") as f:
        f.write(img_bytes)
    try:
        result_text = gpt_infer(save_path, image_reference_prompt)
        result = parse_json_with_retries(result_text)

        if isinstance(result, str):
            raise ValueError("GPT 返回内容非结构化或 JSON 解析失败")

        output_path = os.path.join(DEST_FOLDER, f"{save_name}-image-attribute.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result
    except Exception as e:
        raise RuntimeError(f"图像参考分析失败: {e}")
