from itertools import chain
import re
import sys
from pydantic import Json
import requests
import json
import base64


# Base URL of the Flask app
BASE_URL = 'http://localhost:55500'
SAVE_NAME = "test_run"
def encode_image(path: str) -> str:
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# Test image-to-spec endpoint
def test_image_to_spec(image_path):
    img_b64 = encode_image(image_path)
    payload = {
        "image": img_b64,
        "save_name": SAVE_NAME
    }
    resp = requests.post(f'{BASE_URL}/api/image_to_spec', json=payload)
    resp.raise_for_status()
    data = resp.json()
    print("=== /image_to_spec ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return data['spec']

# Test edit-spec endpoint
def test_edit_spec(spec, text, name='test123'):
    payload = {
        'text': text,
        'spec': spec,
        "save_name": name
    }
    response = requests.post(
        f'{BASE_URL}/api/edit_spec',
        json=payload
    )
    print('edit_spec status:', response.status_code)
    print('Response:', response.json())
    return response.json().get('spec')

# Test combine-spec endpoint
def test_combine_spec(spec_list):
    response = requests.post(
        f'{BASE_URL}/api/combine_spec',
        json={'spec_list': spec_list}
    )
    print('combine_spec status:', response.status_code)
    print('Response:', response.json())
    return response.json().get('spec')

# Test generate-code endpoint
def test_generate_code(spec, save_name='test_run'):
    payload = {
        'spec': spec,
        'save_name': save_name
    }
    response = requests.post(
        f'{BASE_URL}/api/generate_code',
        json=payload
    )
    print('generate_code status:', response.status_code)
    data = response.json()
    print('Response:', data)
    # Save returned code and image if present
    code = data.get('code')
    img_b64 = data.get('render_image')
    if code:
        with open('generated_code.jsx', 'w', encoding='utf-8') as f:
            f.write(code)
        print('Saved generated_code.jsx')
    if img_b64:
        img_bytes = base64.b64decode(img_b64)
        with open('render_image.png', 'wb') as f:
            f.write(img_bytes)
        print('Saved render_image.png')
    return data

def test_init_ui_generation(user_text, save_name="intent_spec"):
    payload = {
        "text": user_text,
        "save_name": save_name
    }
    response = requests.post(
        f'{BASE_URL}/api/init_ui_generation',
        json=payload
    )
    print('init_ui_generation status:', response.status_code)
    data = response.json()
    # print('Response:', json.dumps(data, ensure_ascii=False, indent=2))

    # Save returned code and image if present
    code = data.get('code') or data.get('data', {}).get('code')
    img_b64 = data.get('render_image') or data.get('data', {}).get('render_image')

    if code:
        with open(f'{save_name}.jsx', 'w', encoding='utf-8') as f:
            f.write(code)
        print(f'Saved {save_name}.jsx')

    if img_b64:
        img_bytes = base64.b64decode(img_b64)
        with open(f'{save_name}_render.png', 'wb') as f:
            f.write(img_bytes)
        print(f'Saved {save_name}_render.png')

    return data

def generate_code_from_image(image_path, save_name="default", api_base="http://localhost:55500/api"):
    try:
        # 读取图像并编码为 base64
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        # Step 1: 请求 /api/image_to_spec
        spec_payload = {
            "image": img_b64,
            "save_name": save_name
        }
        spec_response = requests.post(f"{api_base}/image_to_spec", json=spec_payload)
        spec_data = spec_response.json()
        if not spec_response.ok or not spec_data.get("success"):
            return {"error": "Spec generation failed", "details": spec_data}

        spec = spec_data["data"]["spec"]

        # Step 2: 请求 /api/generate_code
        code_payload = {
            "spec": spec,
            "save_name": save_name
        }
        code_response = requests.post(f"{api_base}/generate_code", json=code_payload)
        code_data = code_response.json()
        if not code_response.ok or not code_data.get("success"):
            return {"error": "Code generation failed", "details": code_data}

        return {
            "spec": spec,
            "code": code_data["data"]["code"],
            "render_image": code_data["data"]["render_image"]
        }

    except Exception as e:
        return {"error": "Exception occurred", "details": str(e)}


if __name__ == '__main__':
    # test_init_ui_generation("Create a login page with username and password fields, a submit button, and a logo at the top.", save_name="login_page")
    # from pathlib import Path
    # image_dir = Path("/media/sda5/cyn-workspace/group/group2")
    # image_list_path = list(chain(
    #     image_dir.glob("*.jpg"),
    #     image_dir.glob("*.png")
    # ))
    # # image_list_path = [Path("/media/sda5/cyn-workspace/group/group2/page_spec_7.png")]
    # for image_path in image_list_path:
    #     print(f"Processing {image_path}...")
    #     generate_code_from_image(str(image_path), save_name=f'{image_path.stem}-non-parametric')
    # image_path = "/media/sda5/cyn-workspace/UI-SPEC/spec_generate
    # generate_code_from_image("/media/sda5/cyn-workspace/UI-SPEC/spec_generate_test/example2.png", save_name="my_image_spec")
    # 目标 URL
    from pathlib import Path

    url = 'http://localhost:55500/api/init_ui_generation'
    spec_path = Path("/media/sda5/cyn-workspace/spec.json")
    # 读取本地 spec.json
    try:
        with spec_path.open("r", encoding="utf-8") as f:
            spec = json.load(f)
    except Exception as e:
        print(f"读取 {spec_path} 失败：{e}")
        sys.exit(1)

    payload = {
        "spec": spec,                 # 必填
        "save_name": "intent_spec"    # 可改；不传也行，后端会用默认值
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"请求失败：{e}")
        sys.exit(1)

    # 解析与打印返回
    try:
        data = resp.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except ValueError:
        print("返回不是合法JSON：")
        print(resp.text)