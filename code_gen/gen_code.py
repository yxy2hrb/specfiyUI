import os
import re
import json
from utils.gpt_api import gpt_infer, gpt_infer_no_image

def gen_spec_code(image_path, output_dir, spec_prompt: str, code_prompt: str):
    """
    通过输入图片生成 spec，然后根据 spec 生成代码，并把结果保存为 JSON 文件。

    参数:
      - image_path: 输入图片路径
      - output_dir: 保存 JSON 的目录
      - spec_prompt: 用于从图片生成 spec 的提示
      - code_prompt: 用于从 spec 生成代码的提示，其中包含占位符 '{spec_input}'
    
    返回:
      - (extracted_code, extracted_spec)：提取出的代码字符串和 spec 字符串
    """
    # 1. 生成 spec，最多尝试 3 次，直到 non-empty
    extracted_spec = ""
    spec_res = ""
    for attempt_spec in range(1, 4):
        spec_res = gpt_infer(image_path, spec_prompt)
        print(spec_res)
        spec_match = re.search(r'```spec\n(.*?)\n```', spec_res, re.DOTALL)
        if spec_match:
            extracted_spec = spec_match.group(1).strip()
            print(f"✅ 第 {attempt_spec} 次尝试成功获取 spec")
            break
        else:
            extracted_spec = ""
            if attempt_spec < 3:
                print(f"⚠️ 第 {attempt_spec} 次未找到有效的 spec 块，准备重试")
            else:
                raise ValueError("无法从图片中提取到有效的 spec，请检查图片或提示内容")

    # 2. 根据提取的 spec 拼接 code_prompt
    formatted_code_prompt = code_prompt.replace('{spec_input}', extracted_spec)

    # 3. 多次尝试生成代码并从返回结果中提取出 ```jsx ... ``` 中的代码
    extracted_code = None
    code_res = ""
    for attempt in range(1, 4):
        code_res = gpt_infer_no_image(formatted_code_prompt)
        code_match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        if code_match:
            extracted_code = code_match.group(1).strip()
            print(f"✅ 第 {attempt} 次尝试提取到有效代码")
            break
        else:
            extracted_code = "Error: No valid code block found"
            if attempt < 3:
                print(f"⚠️ 第 {attempt} 次未找到有效代码块，准备重试")
            else:
                raise ValueError("无法提取到有效的代码，请检查 spec 或提示内容")

    # 4. 保存 JSON 到 output_dir
    os.makedirs(output_dir, exist_ok=True)
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f"{image_name}_spec_code.json")

    data = {
        "image_path": image_path,
        "extracted_spec": extracted_spec,
        "extracted_code": extracted_code
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ 数据已保存到 {json_path}")
    return extracted_code, extracted_spec



def gen_code_with_spec(save_name, spec, output_dir, code_prompt: str):
    """
    给定图片路径和已有的 spec 文件，读取 spec 后生成代码，并把结果保存为 JSON 文件。

    参数:
      - image_path: 输入图片路径（可用于记录日志或在 JSON 中保存）
      - spec_path: 存放 spec 文本的文件路径（纯文本文件）
      - output_dir: 保存 JSON 的目录
      - code_prompt: 用于从 spec 生成代码的提示，其中包含占位符 '{spec_input}'
    
    返回:
      - extracted_code：提取出的代码字符串
    """
    # 1. 从 spec_path 读取 spec 内容
    if spec is not None:
        print("✅ 从 spec 文件读取到 spec 内容")

    extracted_spec = str(spec)
    # 2. 根据 spec 拼接 code_prompt
    formatted_code_prompt = code_prompt.replace('{spec_input}', extracted_spec)

    # 3. 多次尝试生成代码并从返回结果中提取出 ```jsx ... ``` 中的代码
    extracted_code = None
    code_res = ""
    for attempt in range(1, 4):
        code_res = gpt_infer_no_image(formatted_code_prompt)
        # code_match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        code_match = re.search(r'```jsx\n(.*?)(\n```|$)', code_res, re.DOTALL)
        if code_match:
            extracted_code = code_match.group(1).strip()
            print(f"✅ 第 {attempt} 次尝试提取到有效代码")
            break
        else:
            extracted_code = "Error: No valid code block found"
            if attempt < 3:
                print(f"⚠️ 第 {attempt} 次未找到有效代码块，准备重试")
            else:
                print("⚠️ 第 3 次尝试仍未找到有效代码块，停止重试")

    # 4. 保存 JSON 到 output_dir
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"{save_name}_code.json")

    data = {
        "extracted_spec": extracted_spec,
        "extracted_code": extracted_code
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ 数据已保存到 {json_path}")
    return extracted_code

def gen_code_with_spec_ori_code(save_name, spec, output_dir, code_prompt: str):
    """
    给定图片路径和已有的 spec 文件，读取 spec 后生成代码，并把结果保存为 JSON 文件。

    参数:
      - image_path: 输入图片路径（可用于记录日志或在 JSON 中保存）
      - spec_path: 存放 spec 文本的文件路径（纯文本文件）
      - output_dir: 保存 JSON 的目录
      - code_prompt: 用于从 spec 生成代码的提示，其中包含占位符 '{spec_input}'
    
    返回:
      - extracted_code：提取出的代码字符串
    """
    # 1. 从 spec_path 读取 spec 内容
    if spec is not None:
        print("✅ 从 spec 文件读取到 spec 内容")
    ori_code_path = "/media/sda5/cyn-workspace/UI-SPEC/my-app/src/App.js"
    with open(ori_code_path, 'r', encoding='utf-8') as f:
        ori_code = f.read()
    extracted_spec = str(spec)
    # 2. 根据 spec 拼接 code_prompt
    formatted_code_prompt = code_prompt.replace('{spec_input}', extracted_spec).replace('{ori_code}', ori_code)

    # 3. 多次尝试生成代码并从返回结果中提取出 ```jsx ... ``` 中的代码
    extracted_code = None
    code_res = ""
    for attempt in range(1, 4):
        code_res = gpt_infer_no_image(formatted_code_prompt)
        # code_match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        code_match = re.search(r'```jsx\n(.*?)(\n```|$)', code_res, re.DOTALL)
        if code_match:
            extracted_code = code_match.group(1).strip()
            print(f"✅ 第 {attempt} 次尝试提取到有效代码")
            break
        else:
            extracted_code = "Error: No valid code block found"
            if attempt < 3:
                print(f"⚠️ 第 {attempt} 次未找到有效代码块，准备重试")
            else:
                print("⚠️ 第 3 次尝试仍未找到有效代码块，停止重试")

    # 4. 保存 JSON 到 output_dir
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"{save_name}_code.json")

    data = {
        "extracted_spec": extracted_spec,
        "extracted_code": extracted_code
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ 数据已保存到 {json_path}")
    return extracted_code
