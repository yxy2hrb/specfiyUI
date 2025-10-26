import json
import os
import jsonpatch
import httpx
from openai import OpenAI
from utils.gpt_api import gpt_infer_no_image
from utils.edit_prompt import *
import re
SPEC_RESULTS = "/media/sda5/cyn-workspace/UI-SPEC/backend_results/spec-results"
os.makedirs(SPEC_RESULTS, exist_ok=True)

def get_ui_spec_tree(spec: str, name: str):
    """
    尝试调用大模型 (gpt_infer_no_image) 三次，将 Python JSONDecodeError 信息当作 prompt 附加到模板里，
    以提高模型输出合法 JSON 的几率。返回解析后的 Python 对象或 None。
    """

    # 假定 spec_to_structured_prompt 中包含了 "{user input}" 占位符，我们在失败后再追加 "{error message}"
    base_template = spec_to_structured_prompt  # 例如："... 请输出严格符合 JSON 标准的内容：\n{user input} ..."
    error_suffix_template = (
        "\n\n---\n"
        "注意：上次输出的 JSON 在本地解析时报错为：\n"
        "{error message}\n"
        "请根据上述错误信息修正你的 JSON，只返回一个正确的 JSON 对象。"
    )

    for attempt in range(1, 5):
        # 第一次尝试，只使用原始的 spec；后续尝试如果有 error_msg 会追加到 prompt
        spec = str(spec)
        if attempt == 1:
            prompt = base_template.replace("{user input}", spec)
        else:
            # 上一次的 error_msg 会保存在 `last_error` 里
            prompt = (
                base_template.replace("{user input}", spec)
                + error_suffix_template.replace("{error message}", last_error)
            )

        # 调用大模型
        response = gpt_infer_no_image(prompt)

        # 提取 code block 中的 JSON 文本
        match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response, re.DOTALL)
        if not match:
            # 如果连代码块都没有，直接记录一个通用提示
            last_error = "没有检测到任何 ` ```json ... ``` ` 代码块"
            continue

        extracted_json_text = match.group(1).strip()
        print(f"✅ 第 {attempt} 次尝试提取到原始 JSON 文本：\n{extracted_json_text}\n")

        # 尝试将提取的字符串解析为 Python 对象
        try:
            parsed = json.loads(extracted_json_text)
        except json.JSONDecodeError as e:
            last_error = str(e)
            print(f"❌ JSON 解析失败（第 {attempt} 次）：{last_error}")
            # 继续下一轮循环，利用 last_error 在下一次 prompt 中告诉模型
            continue

        # 解析成功，将其写入文件并返回 parsed 对象
        with open(f"{name}.json", "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)

        return parsed, f"{name}.json"

    # 三次尝试均失败，返回 None
    return None

def edit_ui_spec(user_request: str,
                 spec_path: str = "ui_spec_tree.json"):
    """
    根据用户的编辑需求调用 LLM，生成 JSON Patch 并应用到 ui_spec_tree.json。
    增加错误修复处理，确保生成合法的 JSON Patch。
    """
    # 加载原始 UI Spec
    with open(spec_path, "r", encoding="utf-8") as f:
        ui_spec = json.load(f)

    # 构造提示
    system_prompt = (
        "你是一个帮助用户编辑 UI Spec Tree 的助手。\n\n"
        "输入：用户的编辑需求，例如 “帮我加到 sidebar 的纵向间距 24px”。\n"
        "输出：符合 JSON Patch 标准的数组，包含要对原始 spec 进行的操作。\n\n"
        "示例：\n"
        "用户：\"帮我加到 sidebar 的纵向间距 24px\"\n"
        "助手输出：\n"
        "[\n"
        "  {\"op\": \"add\", \"path\": \"/components/sidebar/spacing/vertical\", \"value\": \"24px\"}\n"
        "]\n\n"
        "不要输出除 JSON Patch 以外的内容。\n"
        "要注意不要直接添加spec中不存在的路径，如果存在多个key分开完成操作"
    )

    last_error = None
    for attempt in range(1, 5):
        # 合成消息
        prompt = f"{system_prompt}\nUI SPEC Tree:{ui_spec}\n用户：{user_request}"
        if last_error:
            prompt += f"\n---\n注意：上次输出的 JSON Patch 在解析时报错：\n{last_error}"

        # 调用 LLM 生成 Patch
        patch_text = gpt_infer_no_image(prompt).strip()

        # 尝试解析 JSON Patch
        try:
            patch_ops = json.loads(patch_text)
            break
        except Exception as e:
            last_error = f"JSON解析失败：{e}\nLLM输出：{patch_text}"
            print(f"❌ 第 {attempt} 次尝试解析失败，错误信息：{last_error}")
            continue
    else:
        raise RuntimeError(f"多次尝试生成合法 JSON Patch 失败。\n最后的错误信息：{last_error}")

    # 应用 Patch
    ui_spec = jsonpatch.apply_patch(ui_spec, patch_ops)

    # 保存更新后的 Spec
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(ui_spec, f, ensure_ascii=False, indent=2)

    print("✅ UI Spec 已更新，应用了以下 patch:", patch_ops)
    return ui_spec, spec_path

def edit_ui_spec_v2(user_request: str, ui_spec: str, save_name: str = "ui_spec_tree.json"):
    """
    根据用户的编辑需求调用 LLM，生成 JSON Patch 并应用到 ui_spec_tree.json。
    增加错误修复处理，确保生成合法的 JSON Patch。
    """
    # 构造提示
    system_prompt = (
        "你是一个帮助用户编辑 UI Spec Tree 的助手。\n\n"
        "输入：用户的编辑需求，例如 “帮我加到 sidebar 的纵向间距 24px”。\n"
        "输出：符合 JSON Patch 标准的数组，包含要对原始 spec 进行的操作。\n\n"
        "示例：\n"
        "用户：\"帮我加到 sidebar 的纵向间距 24px\"\n"
        "助手输出：\n"
        "[\n"
        "  {\"op\": \"add\", \"path\": \"components/sidebar/spacing/vertical\", \"value\": \"24px\"}\n"
        "]\n\n"
        "不要输出除 JSON Patch 以外的内容。\n"
        "要注意不要直接添加spec中不存在的路径，如果存在多个key分开完成操作"
    )

    last_error = None
    for attempt in range(1, 5):
        # 合成消息
        prompt = f"{system_prompt}\nUI SPEC Tree:{ui_spec}\n用户：{user_request}"
        if last_error:
            prompt += f"\n---\n注意：上次输出的 JSON Patch 在解析时报错：\n{last_error}"

        # 调用 LLM 生成 Patch
        patch_text = gpt_infer_no_image(prompt).strip()

        # 尝试解析 JSON Patch
        try:
            patch_ops = json.loads(patch_text)
            if not isinstance(ui_spec, dict):
                ui_spec = json.loads(ui_spec)  # 确保 ui_spec 是字典类型
            ui_spec = jsonpatch.apply_patch(ui_spec, patch_ops)
            break
        except Exception as e:
            last_error = f"JSON解析失败：{e}\nLLM输出：{patch_text}"
            print(f"❌ 第 {attempt} 次尝试解析失败，错误信息：{last_error}")
            continue
    else:
        raise RuntimeError(f"多次尝试生成合法 JSON Patch 失败。\n最后的错误信息：{last_error}")
    

    # 保存更新后的 Spec
    with open(os.path.join(SPEC_RESULTS, save_name), "w", encoding="utf-8") as f:
        json.dump(ui_spec, f, ensure_ascii=False, indent=4)

    print("✅ UI Spec 已更新，应用了以下 patch:", patch_ops)
    return ui_spec

# 示例用法
if __name__ == "__main__":
    # all_spec = "/media/sda1/cyn-workspace/UI-SPEC/all_spec_v2.json"
    # all_spec = json.load(open(all_spec, "r", encoding="utf-8"))
    # for spec in all_spec:
    #     name = spec["filename"]
    #     if name != "15330_397106":
    #         continue
    #     spec = spec["spec_res"]
        
    #     spec_tree = get_ui_spec_tree(spec, name)
    #     print(spec_tree)
    user_input = "转换为Airbnb风格，色彩和风格都要相似"
    edit_ui_spec(user_input, spec_path="/media/sda1/cyn-workspace/UI-SPEC/15330_397106.json")