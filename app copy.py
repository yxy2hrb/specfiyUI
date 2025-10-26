from doctest import debug
from email.mime import base
import json
from math import log
from flask import Flask, request, jsonify, render_template, send_from_directory
import base64
import os
import io
from PIL import Image
from utils.gpt_api import gpt_infer, gpt_infer_no_image
import tempfile
from flask_cors import CORS
from utils.prompt import code_prompt_web_v8
from utils.spec_prompt import *
from utils.edit_prompt import merge_prompt
from spec_editor import edit_ui_spec_v2
from code_gen.gen_code import gen_code_with_spec
from code_gen.code_debug import iterative_debug
import time

"""
API：

上传图，提取组件类型
Generate2：根据BBOX的大小关系去重新生成SPEC，根据SPEC生成UI
"""

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
BACKEND_RESULTS = "/media/sda5/cyn-workspace/UI-SPEC/backend_results/image-results"
DEST_FOLDER = f"{BACKEND_RESULTS}/gen_code_result"
CODE_PATH = "/media/sda5/cyn-workspace/UI-SPEC/my-app/src/App.js"
CODE_DIR = "/media/sda5/cyn-workspace/UI-SPEC/my-app"
SCRIPT_PATH  = "/media/sda5/cyn-workspace/UI-SPEC/my-app/src/transform-recharts-animation.js"
WAIT_SELECTOR = "#root"

PORT = 3002
os.makedirs(BACKEND_RESULTS, exist_ok=True)
os.makedirs(DEST_FOLDER, exist_ok=True)

def parse_json_with_retries(spec_res, max_retries=4, wait_time=0.5):
    """
    尝试解析JSON字符串，支持多次重试。
    
    参数:
        spec_res (str): 待解析的JSON字符串。
        max_retries (int): 最大重试次数，默认为4。
        wait_time (float): 每次重试之间等待的秒数，默认为0.5秒。
    
    返回:
        解析成功: 返回解析后的数据对象。
        解析失败: 返回Flask的jsonify错误响应和400状态码。
    """
    attempt = 1

    while attempt <= max_retries:
        try:
            parsed_data = json.loads(spec_res)
            return parsed_data  # 成功解析，返回结果
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON decode error at attempt {attempt}/{max_retries}: {e}")
            if attempt == max_retries:
                return jsonify({'error': 'Invalid JSON format from model response'}), 400
            time.sleep(wait_time)
            attempt += 1

# ---- Helpers: stubs for model/API calls ----
def call_image_to_spec_model(image_bytes, save_name):
    """
    Saves the incoming image with a timestamped filename and calls the GPT-based infer function.
    """
    # Generate timestamp-based filename (milliseconds precision)
    image_path = os.path.join(BACKEND_RESULTS, f"{save_name}.png")

    # Write the image bytes to disk
    with open(image_path, "wb") as f:
        f.write(image_bytes)
        
    spec_res = gpt_infer(image_path, spec_prompt_CYN)
    result  = parse_json_with_retries(spec_res)
    if isinstance(result, tuple):
        # 说明是错误响应，直接return
        return result

    return result

def call_text_edit_model(text, spec, save_name):
    new_spec = edit_ui_spec_v2(text, spec, f"{save_name}-edit.json")
    return new_spec


def call_combine_spec_model(spec_list):
    spec = ",".join(spec_list)
    merge_r = merge_prompt.format(spec_list=spec)
    merge_spec = gpt_infer_no_image(merge_r)
    return merge_spec


def call_spec_to_code_model(spec, save_name):
    max_temp = 4
    temp = 1

    while temp < max_temp:
        # 2. 调用 gen_code_with_spec 生成代码
        extracted_code = gen_code_with_spec(
            save_name,
            spec,
            DEST_FOLDER,
            code_prompt_web_v8
        )
        if extracted_code is None:
            print(f"⚠️ 从 {save_name} 生成代码失败，跳过调试")
        # 将提取出的代码写入 CODE_PATH
            return
        with open(CODE_PATH, "w", encoding="utf-8") as f:
            f.write(extracted_code)
        print("✅ 生成并写入代码成功")

        screenshot_path = os.path.join(DEST_FOLDER, f"{save_name}_screenshot.png")
        # 3. 调用 iterative_debug 进行渲染+调试，并保存截图
        success = iterative_debug(
                    code_path=CODE_PATH,
                    port=PORT,
                    wait_selector=WAIT_SELECTOR,
                    screenshot=screenshot_path,
                    code_dir=CODE_DIR,
                    script_path=SCRIPT_PATH,
                    log_dir=DEST_FOLDER,
                    image_path=DEST_FOLDER
                )

        if success:
            print(f"✅ {save_name} 调试并截图完成：{screenshot_path}")
            break
        else:
            temp += 1
            print(f"❌ {save_name} 调试未成功，尝试第 {temp} 次重试")
    img_base64 = base64.b64encode(open(screenshot_path, "rb").read()).decode('utf-8')
    return extracted_code, img_base64

@app.route('/api/image_to_region', methods=['POST'])
def image_to_region():
    """
    上传图片，提取UI区域划分（按功能区）
    input: base64 image
    output: list of regions and their components
    """
    data = request.get_json()
    img_b64 = data.get('image')
    save_name = data.get('save_name', 'default')

    if not img_b64:
        return jsonify({'error': 'missing image'}), 400

    try:
        img_bytes = base64.b64decode(img_b64)
    except Exception:
        return jsonify({'error': 'invalid base64 image'}), 400

    result_raw = gpt_infer(img_bytes, region_extract_prompt)
    result = parse_json_with_retries(result_raw)

    if isinstance(result, tuple):  # error
        return result

    # save result
    with open(os.path.join(BACKEND_RESULTS, f"{save_name}-region.json"), "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return jsonify({'region_info': r esult})

@app.route('/api/image_to_color', methods=['POST'])
def image_to_color():
    """
    上传图片，提取配色体系
    input: base64 image
    output: color json
    """
    data = request.get_json()
    img_b64 = data.get('image')
    save_name = data.get('save_name', 'default')

    if not img_b64:
        return jsonify({'error': 'missing image'}), 400

    try:
        img_bytes = base64.b64decode(img_b64)
    except Exception:
        return jsonify({'error': 'invalid base64 image'}), 400

    spec_res = gpt_infer(img_bytes, color_extract_prompt)
    result = parse_json_with_retries(spec_res)

    if isinstance(result, tuple):  # 说明是错误响应
        return result

    # 保存结果
    with open(os.path.join(BACKEND_RESULTS, f"{save_name}-color.json"), "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return jsonify({'color': result})

@app.route('/api/image_to_layout', methods=['POST'])
def image_to_layout():
    """
    上传图，提取布局结构信息
    input: base64 image
    output: layout json
    """
    data = request.get_json()
    img_b64 = data.get('image')
    save_name = data.get('save_name', 'default')

    if not img_b64:
        return jsonify({'error': 'missing image'}), 400

    try:
        img_bytes = base64.b64decode(img_b64)
    except Exception:
        return jsonify({'error': 'invalid base64 image'}), 400
    img = Image.open(io.BytesIO(img_bytes))
    width, height = img.size
    if width != 1200 or height != 900:
        return jsonify({'error': 'image size must be 1200x900'}), 400
    spec_res = gpt_infer(img_bytes, layout_extract_prompt)
    result = parse_json_with_retries(spec_res)

    if isinstance(result, tuple):  # 解析失败时返回的是元组 (jsonify, 400)
        return result

    # 保存 layout 分析结果
    with open(os.path.join(BACKEND_RESULTS, f"{save_name}-layout.json"), "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return jsonify({'layout': result})

@app.route('/hello')
def hello():
    # redirect to upload UI
    return "hello world!"

@app.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')

@app.route('/api/text_to_spec', methods=['POST'])
def text_to_spec():
    """
    input: text
    return: spec
    """
    data = request.get_json()
    text = data.get('text')
    save_name = data.get('save_name')
    if not save_name:
        return jsonify({'error': 'missing name'}), 400
    if text is None:
        return jsonify({'error': 'missing text'}), 400
    # call gpt api
    spec = gpt_infer_no_image(text_to_spec_prompt)
    result = parse_json_with_retries(spec)
    if isinstance(result, tuple):
        # 说明是错误响应，直接return
        return result
    spec = result
    with open(os.path.join(BACKEND_RESULTS, f"{save_name}-text-spec.json"), "w") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    return jsonify({'spec': spec})

@app.route('/api/image_reference', methods=['POST'])
def image_reference():# -> tuple[Response, Literal[400]] | tuple | Response:
    """
    input: image
    return: attribute
    """
    data = request.get_json()
    img_b64 = data.get('image')
    spec = data.get('spec')
    save_name = data.get('save_name')
    if not save_name:
        return jsonify({'error': 'missing name'}), 400
    # decode
    try:
        img_bytes = base64.b64decode(img_b64)
    except Exception as e:
        return jsonify({'error': 'invalid base64 image'}), 400
    result = gpt_infer(img_bytes, division_prompt_v0)
    result = parse_json_with_retries(result)
    if isinstance(result, tuple):
        # 说明是错误响应，直接return
        return result
    # save the result
    with open(os.path.join(BACKEND_RESULTS, f"{save_name}-image-attribute.json"), "w") as f:
        json.dump(result, f, ensure_ascii=False, indent = 2)
    return jsonify({'attribute': result})

# @app.route('/api/layout_to_bbox', methods=['POST'])


@app.route('/api/image_to_spec', methods=['POST'])
def image_to_spec():
    data = request.get_json()
    img_b64 = data.get('image')
    spec = data.get('spec')
    save_name = data.get('save_name')
    if not save_name:
        return jsonify({'error': 'missing name'}), 400
    # decode
    try:
        img_bytes = base64.b64decode(img_b64)
    except Exception as e:
        return jsonify({'error': 'invalid base64 image'}), 400
    spec = call_image_to_spec_model(img_bytes, save_name)
    return jsonify({'spec': spec})

@app.route('/api/edit_spec', methods=['POST'])
def edit_spec():
    data = request.get_json()
    save_name = data.get('save_name')
    if not save_name:
        return jsonify({'error': 'missing name'}), 400
    text = data.get('text') # 用户的编辑意图
    spec = data.get('spec') # 完整的SPEC Tree
    if text is None or spec is None:
        return jsonify({'error': 'missing parameters'}), 400
    updated = call_text_edit_model(text, spec, save_name)
    return jsonify({'spec': updated})

@app.route('/api/combine_spec', methods=['POST'])
def combine_spec():
    data = request.get_json()
    spec = data.get('spec')
    save_name = data.get('save_name')
    if not save_name:
        return jsonify({'error': 'missing name'}), 400
    spec_list = data.get('spec_list')
    if not isinstance(spec_list, list):
        return jsonify({'error': 'spec_list must be a list'}), 400
    combined = call_combine_spec_model(spec_list)
    return jsonify({'spec': combined})

@app.route('/api/generate_code', methods=['POST'])
def generate_code():
    data = request.get_json()
    spec = data.get('spec')
    save_name = data.get('save_name')
    if not save_name:
        return jsonify({'error': 'missing name'}), 400
    if spec is None:
        return jsonify({'error': 'missing spec'}), 400
    code, render_img = call_spec_to_code_model(spec, save_name)
    return jsonify({'code': code, 'render_image': render_img})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=55500)
