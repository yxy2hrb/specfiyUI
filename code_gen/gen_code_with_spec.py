import os
import random
import csv
import re
from datetime import datetime
from utils.prompt import *
from utils.gpt_api import gpt_infer, gpt_infer_no_image
import json


def read_code_from_csv(file_path):
    with open('test.csv', newline='') as f:
        reader = csv.reader(f)
    for row in reader:
        original_code = row[0].replace('""', '"')
        print(original_code)
    return original_code

def generate_code_withspec(image_path,spec, output_dir, spec_prompt: str, code_prompt: str):
    '''
    生成 spec 并提取代码，将结果保存为 JSON 文件。
    参数:
      - image_path: 输入图片路径
      - output_dir: 保存 JSON 的目录
    返回:
      - 提取的代码字符串
    '''
    # 1. 生成 spec

    formatted_code_prompt = code_prompt.replace('{spec_input}', spec)

    # 2. 生成代码
    extracted_code = None

    for attempt in range(1, 4):
        # code_res = qwen_code.infer_text(formatted_code_prompt)
        code_res = gpt_infer_no_image(formatted_code_prompt)
        match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        if match:
            extracted_code = match.group(1).strip()
            print(f'✅ 第 {attempt} 次尝试提取到有效代码')
            break
        else:
            extracted_code = 'Error: No valid code block found'
            print(f'⚠️ 第 {attempt} 次未找到有效代码块，准备重试' if attempt < 3 else '⚠️ 第 3 次尝试仍未找到有效代码块')

    # 4. 保存到 JSON
    os.makedirs(output_dir, exist_ok=True)

    # 使用图片文件名（不带扩展名）来命名 JSON
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f'{image_name}_origin_code.json')

    data = {
        'image_path': image_path,
        'spec_res': spec,
        'code_response': code_res,
        'extracted_code': extracted_code
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'✅ 数据已保存到 {json_path}')
    return extracted_code,spec

def generate_code_single(image_path, output_dir, spec_prompt: str, code_prompt: str):
    '''
    生成 spec 并提取代码，将结果保存为 JSON 文件。
    参数:
      - image_path: 输入图片路径
      - output_dir: 保存 JSON 的目录
    返回:
      - 提取的代码字符串
    '''
    # 1. 生成 spec
    spec_res = qwen_image.infer_with_image(image_path, spec_prompt)
    # spec_res = gpt_infer(image_path, spec_prompt)
    match = re.search(r'```spec\n(.*?)\n```', spec_res, re.DOTALL)
    extracted_spec = match.group(1).strip()
    if extracted_spec:
        print('✅ spec 获取成功，开始生成代码')
    else:
        print(' spec 获取失败，开始生成代码')
        return None
    formatted_code_prompt = code_prompt.replace('{spec_input}', extracted_spec)

    # 2. 生成代码
    extracted_code = None

    for attempt in range(1, 4):
        # code_res = qwen_code.infer_text(formatted_code_prompt)
        code_res = gpt_infer_no_image(formatted_code_prompt)
        match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        if match:
            extracted_code = match.group(1).strip()
            print(f'✅ 第 {attempt} 次尝试提取到有效代码')
            break
        else:
            extracted_code = 'Error: No valid code block found'
            print(f'⚠️ 第 {attempt} 次未找到有效代码块，准备重试' if attempt < 3 else '⚠️ 第 3 次尝试仍未找到有效代码块')

    # 4. 保存到 JSON
    os.makedirs(output_dir, exist_ok=True)

    # 使用图片文件名（不带扩展名）来命名 JSON
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f'{image_name}_origin_code.json')

    data = {
        'image_path': image_path,
        'spec_res': spec_res,
        'extracted_code': extracted_code
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'✅ 数据已保存到 {json_path}')
    return extracted_code,spec_res

def generate_code_withrag(image_path, output_dir):
    '''
    生成 spec 并提取代码，将结果保存为 JSON 文件。
    参数:
      - image_path: 输入图片路径
      - output_dir: 保存 JSON 的目录
    返回:
      - 提取的代码字符串
    '''
    # 1. 生成 spec
    spec_res = qwen_image.infer_with_image(image_path, spc_dsx_v2)
    # spec_res = gpt_infer(image_path, spec_prompt)
    match = re.search(r'```spec\n(.*?)\n```', spec_res, re.DOTALL)
    extracted_spec = match.group(1).strip()
    formatted_code_prompt = code_prompt_v2.replace('{spec_input}', extracted_spec)
    formatted_code_prompt+=rag_prompt
    if extracted_spec:
        print('✅ spec 获取成功，开始生成代码')
    else:
        print(' spec 获取失败，开始生成代码')
        return None

    # 2. 生成代码
    extracted_code = None

    for attempt in range(1, 4):
        code_res = qwen_code.infer_text(formatted_code_prompt)
        # code_res = gpt_infer_no_image(formatted_code_prompt)
        match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
        if match:
            extracted_code = match.group(1).strip()
            print(f'✅ 第 {attempt} 次尝试提取到有效代码')
            break
        else:
            extracted_code = 'Error: No valid code block found'
            print(f'⚠️ 第 {attempt} 次未找到有效代码块，准备重试' if attempt < 3 else '⚠️ 第 3 次尝试仍未找到有效代码块')

    # 4. 保存到 JSON
    os.makedirs(output_dir, exist_ok=True)

    # 使用图片文件名（不带扩展名）来命名 JSON
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_dir, f'{image_name}_origin_code.json')

    data = {
        'image_path': image_path,
        'spec_res': spec_res,
        'extracted_code': extracted_code
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'✅ 数据已保存到 {json_path}')
    return extracted_code,spec_res

if __name__ == "__main__":
    extracted_code,spec = generate_code_withrag("/home/c50047709/cyn-workspace/code-generation/data/test_0506/9728_260702.jpg","/home/c50047709/cyn-workspace/code-generation/data/gen_code_withrag_0512")
    print(extracted_code)
    
