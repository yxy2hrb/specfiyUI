import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.gpt_api import gpt_infer_no_image
import llm_infer as svc
import os
import json
import logging

"""
# 1. 结构化属性
# 2. 生成每个layer的bbox，可视化为小图标，作为示意
# 3. 生成SPEC的时候，为每个layer生成bbox，进行定位
"""
"""
user_id
"""
app = Flask(__name__)
CORS(app)

BACKEND_RESULTS = "/media/sda5/cyn-workspace/UI-SPEC/backend_results/image-results"
os.makedirs(BACKEND_RESULTS, exist_ok=True)

def response(success, data=None, error=None):
    return jsonify({"success": success, "data": data, "error": error}), 200 if success else 400

@app.route('/api/image_to_spec', methods=['POST'])
def api_image_to_spec():
    data = request.get_json()
    img_b64 = data.get('image')
    print(f"Received image of length: {img_b64[:100]}")
    save_name = data.get('save_name', 'default')
    try:
        img_bytes = svc.decode_image(img_b64)
        save_path = os.path.join(BACKEND_RESULTS, f"{save_name}.png")
        spec = svc.image_to_spec(img_bytes, save_path)
        if not spec:
            return response(False, error="Failed to parse image to spec")
        return response(True, {"spec": spec})
    except Exception as e:
        print(f"Error processing image: {e}")
        return response(False, error=str(e))

logger = logging.getLogger(__name__)

CODE_FENCE_JSON = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)
SAFE_NAME_RE = re.compile(r"^[\w\-.]{1,64}$")  # 仅字母/数字/_/-/.，且长度限制

def error_response(message: str, http_status: int = 400):
    return jsonify({"success": False, "error": message}), http_status

def parse_json_from_text(text: str):
    """
    先尝试从 ```json ... ``` 中提取；否则尝试把整体当作 JSON 解析。
    解析失败直接抛出 ValueError，由上层捕获。
    """
    if not isinstance(text, str):
        raise ValueError("LLM返回类型异常：非字符串")
    m = CODE_FENCE_JSON.search(text)
    candidate = m.group(1).strip() if m else text.strip()
    # 防止一些模型末尾多逗号或 BOM 等情况
    candidate = candidate.strip("\ufeff \n\r\t")
    return json.loads(candidate)

def ensure_dict(name: str, value):
    if not isinstance(value, dict):
        raise ValueError(f"{name} 必须是对象（JSON dict）")
    
@app.route('/api/init_ui_generation', methods=['POST'])
def api_init_ui_generation():
    # 1) 基础请求校验
    if not request.is_json:
        return error_response("请求头Content-Type必须为application/json", 415)

    data = request.get_json(silent=True)
    if data is None:
        return error_response("请求体JSON解析失败", 400)

    # 2) 字段校验
    user_spec = data.get("spec")
    if user_spec is None:
        return error_response("缺少必填字段：spec", 400)
    if not isinstance(user_spec, dict):
        return error_response("spec必须为对象（JSON dict）", 400)

    save_name = data.get("save_name", "intent_spec")
    
    
    if not isinstance(save_name, str) or not SAFE_NAME_RE.match(save_name):
        return error_response("save_name不合法：仅支持字母/数字/_/-/.，长度1~64", 400)
    # usage_scenario_prompt = (
    #     "用户正在设计一个创新的UI，请帮助用户细化设计场景。"
    #     "举个例子：用户输入：帮我设计一个创新的社交AI的数据监控平台"
    #     "输出：```json {{\"Usage_Scenario\": 这是一个面向社交AI运营团队的数据监控平台，核心功能包括："
    #     "1. 实时用户互动趋势图（折线图），按分钟/小时统计互动数量。"
    #     "2. 情感分析分布图（饼图或环形图），显示正面、中性、负面情绪比例。"
    #     "3. AI响应延迟监控（柱状图），按时间段显示平均响应时长。"
    #     "4. 热点话题词云与关键词出现频率对比（柱状图+词云结合）。"
    #     "5. 用户地域分布（地图+热力图），按地区显示用户活跃度。"
    #     "6. 历史趋势回溯功能，可用折线图和面积图对比过去7天、30天数据。"
    #     "7. 异常检测预警列表，结合折线图标记异常峰值。"
    #     "平台支持通过标签筛选数据，并在不同图表间联动更新。}}```"
    #     "用户输入是:{user_input}\n"
    #     "输出: ```json ```"
    # )
    # usage_guide_prompt = (
    #     "请你根据UI_Design_Specification中的Usage_Scenario来"
    #     "修改所有组件的Function，使Function准确对应Usage_Scenario"
    #     "请输出 JSON 格式的 Usage_Scenario JSON 格式正确无误。用户输入如下：{user_input}\n"
    #     "输出格式: ```json {{\"Usage_Scenario\": {{ ... }} }}```"
    # )
    # user_input = user_spec["UI_Design_Specification"]["Usage_Scenario"]
    # updated_usage_scenario = usage_guide_prompt.format(user_input=user_input)
    # updated_usage_scenario = gpt_infer_no_image(updated_usage_scenario, model='gpt')
    # try:
    #     extracted_dict = parse_json_from_text(updated_usage_scenario)
    #     ensure_dict("Usage_Scenario", extracted_dict)
    # except ValueError as ve:
    #     logger.warning("解析LLM返回失败：%s", ve)
    #     return error_response(f"解析模型返回的Usage_Scenario失败：{ve}", 422)
    # except Exception as e:
    #     logger.exception("未知错误：解析LLM返回")
    #     return error_response(f"解析模型返回异常：{e}", 500)

    # user_spec["UI_Design_Specification"]["Usage_Scenario"] = extracted_dict["Usage_Scenario"]
    # 3) 生成提示词，并调用模型（注意修正了原代码中的未定义变量 spec）
    prompt = (
    "请你根据 UI_Design_Specification 来重新生成 Page_Composition。"
    "UI_Design_Specification中包含Color_System, Usage_Scenario, Layout_Structure, Shape_Language",
    "使用Color_System修改Color_Scheme，使用Usage_Scenario修改Function，使用Layout_Structure修改Component_Layout_Style和Component_Layout_in_Section和Section_Position_on_Page",
    "要求是修改之后的UI_Design_Specification和Page_Composition统一和谐，表达一致的设计信息、布局和色彩"
    "请输出 JSON 格式的 Page_Composition，确保 JSON 格式正确无误。用户输入如下：{user_input}\n"
    "输出格式: ```json {{\"Page_Composition\": {{ ... }} }}```"
)

    refine_prompt = prompt.format(user_input=user_spec)

    try:
        page_composition_updated = gpt_infer_no_image(refine_prompt, model='gpt')
    except Exception as e:
        logger.exception("调用LLM失败")
        return error_response(f"调用模型失败：{e}", 502)

    # 4) 解析并验证 LLM 返回的 JSON
    try:
        extracted_dict = parse_json_from_text(page_composition_updated)
        ensure_dict("Page_Composition", extracted_dict)
    except ValueError as ve:
        logger.warning("解析LLM返回失败：%s", ve)
        return error_response(f"解析模型返回的Page Composition失败：{ve}", 422)
    except Exception as e:
        logger.exception("未知错误：解析LLM返回")
        return error_response(f"解析模型返回异常：{e}", 500)

    # 写回到 user_spec
    user_spec = dict(user_spec)  # 浅拷贝避免副作用
    user_spec["Page_Composition"] = extracted_dict["Page_Composition"]

    # 5) 下游代码生成
    try:
        code, image = svc.generate_code(user_spec, save_name)
    except Exception as e:
        logger.exception("代码生成服务异常")
        return error_response(f"代码生成服务异常：{e}", 502)

    if not code:
        return error_response("代码生成失败", 500)

    # 6) 成功返回
    return jsonify({
        "success": True,
        "data": {
            "code": code,
            "render_image": image,
            "spec": user_spec
        }
    }), 200

# @app.route('/api/intent_to_spec', methods=['POST'])
# def api_intent_to_spec():
#     """
#     接收用户自然语言意图（含组件/布局/样式/目标）→ 返回结构化UI设计SPEC
#     """
#     data = request.get_json()
#     user_text = data.get("text")
#     save_name = data.get("save_name", "intent_spec")

#     if not user_text:
#         return jsonify({"success": False, "error": "缺少设计意图文本"}), 400

#     spec = svc.generate_spec_from_intent(user_text)
#     if not spec:
#         return jsonify({"success": False, "error": "生成SPEC失败"}), 400

#     output_path = os.path.join("/media/sda5/cyn-workspace/UI-SPEC/backend_results/image-results", f"{save_name}-intent-spec.json")
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(spec, f, ensure_ascii=False, indent=2)

#     return jsonify({"success": True, "data": {"spec": spec}})

# @app.route('/api/image_reference', methods=['POST'])
# def api_image_reference():
#     """
#     接收图像和 UI spec，返回图像属性结构
#     """
#     data = request.get_json()
#     # app.logger.info(f"Received data: {data}")  # 添加日志
#     img_b64 = data.get('image')
#     spec = data.get('spec', None)  # 当前没用，但保留接口一致性
#     save_name = data.get('save_name', 'image_reference')

#     if not img_b64 or not save_name:
#         return response(False, error="缺少 image 或 save_name 参数")

#     try:
#         result = svc.analyze_image_reference(img_b64, spec, save_name)
#         return response(True, {"attribute": result})
#     except Exception as e:
#         return response(False, error=str(e))

# @app.route('/api/text_to_spec', methods=['POST'])
# def api_text_to_spec():
#     data = request.get_json()
#     text = data.get('text')
#     spec = svc.text_to_spec(text)
#     if not spec:
#         return response(False, error="Failed to convert text to spec")
#     return response(True, {"spec": spec})

@app.route('/api/edit_spec', methods=['POST'])
def api_edit_spec():
    data = request.get_json()
    spec,code = svc.edit_spec(data.get('text'), data.get('spec'), data.get('save_name'))
    return response(True, {"spec": spec,"extracted_code":code})

# @app.route('/api/combine_spec', methods=['POST'])
# def api_combine_spec():
#     data = request.get_json()
#     combined = svc.combine_specs(data.get('spec_list'))
#     if not combined:
#         return response(False, error="Spec merge failed")
#     return response(True, {"spec": combined})

@app.route('/api/generate_code', methods=['POST'])
def api_generate_code():
    data = request.get_json()
    code, image = svc.generate_code(data.get('spec'), data.get('save_name'))
    if not code:
        return response(False, error="Code generation failed")
    return response(True, {"code": code, "render_image": image})

@app.route('/hello')
def hello():
    return "hello world!"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=55500)
