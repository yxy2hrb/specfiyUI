import os
import time
import json

from httpx import get
from code_gen.code_debug import iterative_debug, iterative_debug_v2
from code_gen.gen_code import gen_code_with_spec, gen_spec_code
from spec_editor import edit_ui_spec, get_ui_spec_tree
from utils.prompt import *

def batch_process_images(
    src_folder: str,
    code_path: str,
    port: int,
    wait_selector: str,
    dest_folder: str,
    spec_prompt: str,
    code_prompt: str
):
    """
    批量处理仅图片输入：
      1. 对 src_folder 中的每张图片，调用 generate_code_single(image_path, dest_folder, spec_prompt, code_prompt)
         生成对应的 spec_res 和 extracted_code。
      2. 将 extracted_code 写入 code_path。
      3. 调用 iterative_debug 进行渲染+调试，将截图保存在 dest_folder。
      4. 如果目标截图已存在，则跳过该图片。

    参数:
      - src_folder: 存放输入图片的目录（支持 .jpg/.jpeg/.png）
      - code_path: 渲染/调试时所需的前端代码文件路径（例如 App.js）
      - port: iterative_debug 使用的本地服务器端口号
      - wait_selector: iterative_debug 等待的 DOM 选择器 (如 "#root")
      - dest_folder: 保存生成的 JSON 与截图的目录
      - spec_prompt: 传给 generate_code_single 用于从图片生成 spec 的提示语
      - code_prompt: 传给 generate_code_single 用于从 spec 生成代码的提示语（包含 '{spec_input}' 占位符）
    """
    if not os.path.isdir(src_folder):
        print(f"⚠️ 源图片文件夹不存在：{src_folder}")
        return

    os.makedirs(dest_folder, exist_ok=True)

    for fname in os.listdir(src_folder):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        
        base_name = os.path.splitext(fname)[0]
        # 目标截图路径 (以 .png 形式保存)
        screenshot_path = os.path.join(dest_folder, f"{base_name}.png")

        # 如果截图已存在，则跳过
        if os.path.exists(screenshot_path):
            print(f"⏭️ {fname} 的截图已存在，跳过")
            continue

        # 稍作等待，避免请求过快
        time.sleep(1)

        image_path = os.path.join(src_folder, fname)
        print(f"\n🔄 处理图片：{image_path}")

        try:
            # 调用 generate_code_single，只输入 image_path
            extracted_code, spec_res = gen_spec_code(
                image_path,
                dest_folder,
                spec_prompt,
                code_prompt
            )
            if extracted_code is None:
                print(f"⚠️ 从 {fname} 生成代码失败，跳过调试")
                continue

            # 将提取出的代码写入 code_path（覆盖现有文件）
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(extracted_code)
            print("✅ 生成并写入代码成功")
        except Exception as e:
            print(f"⚠️ 从 {fname} 生成或写入代码时出错：{e}")
            continue

        # 2. 调用 iterative_debug 进行渲染+调试，并保存截图
        success = iterative_debug(
            code_path=code_path,
            port=port,
            wait_selector=wait_selector,
            screenshot=screenshot_path,
            log_dir=dest_folder
        )

        if success:
            print(f"✅ {fname} 调试并截图完成：{screenshot_path}")
        else:
            print(f"❌ {fname} 调试未成功，请检查生成的 JSON 和 GPT 建议")


def batch_process_specs(
    src_folder: str,
    code_path: str,
    port: int,
    wait_selector: str,
    dest_folder: str,
    code_prompt: str
):
    """
    批量处理仅已有 spec 输入：
      1. 对 src_folder 中的每个 JSON 文件，解析出其中的 spec_res 和 image_path，
         调用 gen_code_with_spec(image_path, spec_path, dest_folder, code_prompt) 生成 extracted_code。
      2. 将 extracted_code 写入 code_path。
      3. 调用 iterative_debug 进行渲染+调试，将截图保存在 dest_folder。
      4. 如果目标截图已存在，则跳过该 spec。

    参数:
      - src_folder: 存放 spec JSON 文件的目录（每个 JSON 必须包含 "spec_res" 与 "image_path" 字段）
      - code_path: 渲染/调试时所需的前端代码文件路径（例如 App.js）
      - port: iterative_debug 使用的本地服务器端口号
      - wait_selector: iterative_debug 等待的 DOM 选择器 (如 "#root")
      - dest_folder: 保存生成的 JSON 与截图的目录
      - code_prompt: 传给 gen_code_with_spec 用于从 spec 生成代码的提示语（包含 '{spec_input}' 占位符）
    """
    if not os.path.isdir(src_folder):
        print(f"⚠️ 源 spec 文件夹不存在：{src_folder}")
        return

    os.makedirs(dest_folder, exist_ok=True)

    for fname in os.listdir(src_folder):
        if not fname.lower().endswith(".json"):
            continue

        base_name = os.path.splitext(fname)[0]
        # 目标截图路径 (以 .png 形式保存)
        screenshot_path = os.path.join(dest_folder, f"{base_name}.png")

        # 如果截图已存在，则跳过
        if os.path.exists(screenshot_path):
            print(f"⏭️ {fname} 对应的截图已存在，跳过")
            continue

        time.sleep(1)

        spec_path = os.path.join(src_folder, fname)
        print(f"\n🔄 处理 spec 文件：{spec_path}")

        try:
            # 1. 从 JSON 中读取 spec_res 和 image_path
            with open(spec_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            extracted_spec = data.get("spec_res", "").strip()
            image_path = data.get("image_path", "").strip()
            if not extracted_spec:
                print(f"⚠️ {fname} 中未找到 spec_res 字段，跳过")
                continue
            if not image_path or not os.path.isfile(image_path):
                print(f"⚠️ {fname} 中的 image_path 无效，跳过")
                continue

            # 2. 调用 gen_code_with_spec 生成代码
            extracted_code = gen_code_with_spec(
                image_path,
                spec_path,
                dest_folder,
                code_prompt
            )
            if extracted_code is None:
                print(f"⚠️ 从 {fname} 生成代码失败，跳过调试")
                continue

            # 将提取出的代码写入 code_path
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(extracted_code)
            print("✅ 生成并写入代码成功")
        except Exception as e:
            print(f"⚠️ 读取或生成 {fname} 时出错：{e}")
            continue

        # 3. 调用 iterative_debug 进行渲染+调试，并保存截图
        success = iterative_debug(
            code_path=code_path,
            port=port,
            wait_selector=wait_selector,
            screenshot=screenshot_path,
            log_dir=dest_folder
        )

        if success:
            print(f"✅ {fname} 调试并截图完成：{screenshot_path}")
        else:
            print(f"❌ {fname} 调试未成功，请查看 JSON 和 GPT 建议")

def batch_process_json(spec_json_path, 
                       code_path, 
                       port, 
                       wait_selector, 
                       dest_folder, 
                       code_prompt):
    spec_json = json.load(open(spec_json_path, 'r')) if isinstance(spec_json_path, str) else spec_json_path
    for spec in spec_json:
        file_name = spec.get("filename", "unknown_spec")
        if file_name != "15330_397106":
            continue  # 仅处理特定文件名
        screenshot_path = os.path.join(dest_folder, f"{file_name}.png")
        extracted_spec = spec.get("spec_res", "").strip()
        try:

            # 2. 调用 gen_code_with_spec 生成代码
            extracted_code = gen_code_with_spec(
                file_name,
                extracted_spec,
                dest_folder,
                code_prompt
            )
            if extracted_code is None:
                print(f"⚠️ 从 {file_name} 生成代码失败，跳过调试")
                continue

            # 将提取出的代码写入 code_path
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(extracted_code)
            print("✅ 生成并写入代码成功")
        except Exception as e:
            print(f"⚠️ 读取或生成 {file_name} 时出错：{e}")
            continue

        # 3. 调用 iterative_debug 进行渲染+调试，并保存截图
        success = iterative_debug(
            code_path=code_path,
            port=port,
            wait_selector=wait_selector,
            screenshot=screenshot_path,
            log_dir=dest_folder
        )

        if success:
            print(f"✅ {file_name} 调试并截图完成：{screenshot_path}")
        else:
            print(f"❌ {file_name} 调试未成功，请查看 JSON 和 GPT 建议")

def process_single_json(spec_json_path, 
                        save_file_name,
                       code_path, 
                       port, 
                       wait_selector, 
                       dest_folder, 
                       code_prompt):
    spec = json.load(open(spec_json_path, 'r')) if isinstance(spec_json_path, str) else spec_json_path

    file_name = save_file_name

    screenshot_path = os.path.join(dest_folder, f"{file_name}.png")
    try:
        # 2. 调用 gen_code_with_spec 生成代码
        extracted_code = gen_code_with_spec(
            file_name,
            spec,
            dest_folder,
            code_prompt
        )
        if extracted_code is None:
            print(f"⚠️ 从 {file_name} 生成代码失败，跳过调试")
            return
        # 将提取出的代码写入 code_path
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(extracted_code)
        print("✅ 生成并写入代码成功")
    except Exception as e:
        print(f"⚠️ 读取或生成 {file_name} 时出错：{e}")
        return

    # 3. 调用 iterative_debug 进行渲染+调试，并保存截图
    success = iterative_debug(
        code_path=code_path,
        port=port,
        wait_selector=wait_selector,
        screenshot=screenshot_path,
        log_dir=dest_folder
    )

    if success:
        print(f"✅ {file_name} 调试并截图完成：{screenshot_path}")
    else:
        print(f"❌ {file_name} 调试未成功，请查看 JSON 和 GPT 建议")


def process_spec_with_edit(spec_json_path, 
                        save_file_name,
                       code_path, 
                       port, 
                       wait_selector, 
                       dest_folder, 
                       code_prompt, 
                       gen_spec_tree=False,
                       edit_prompt=None):
    file_name = save_file_name
    
    screenshot_path = os.path.join(dest_folder, f"{file_name}.png")
    
    if os.path.exists(screenshot_path):
        print(f"⏭️ {file_name} 的截图已存在，跳过")
        return
    spec = json.load(open(spec_json_path, 'r')) if isinstance(spec_json_path, str) else spec_json_path
    if gen_spec_tree:
        # 1. 生成 UI Spec 树
        print("🔄 生成 UI Spec 树...")
        spec, spec_path = get_ui_spec_tree(spec, save_file_name)
    if edit_prompt is not None and gen_spec_tree:
        spec, spec_path = edit_ui_spec(edit_prompt, spec_path)

    max_temp = 4
    temp = 1

    while temp < max_temp:
        # 2. 调用 gen_code_with_spec 生成代码
        extracted_code = gen_code_with_spec(
            file_name,
            spec,
            dest_folder,
            code_prompt
        )
        if extracted_code is None:
            print(f"⚠️ 从 {file_name} 生成代码失败，跳过调试")
            return
        # 将提取出的代码写入 code_path
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(extracted_code)
        print("✅ 生成并写入代码成功")


        # 3. 调用 iterative_debug 进行渲染+调试，并保存截图
        success = iterative_debug_v2(
            code_path=code_path,
            port=port,
            wait_selector=wait_selector,
            screenshot=screenshot_path,
            log_dir=dest_folder
        )

        if success:
            print(f"✅ {file_name} 调试并截图完成：{screenshot_path}")
            return
        else:
            temp += 1
            print(f"❌ {file_name} 调试未成功，尝试第 {temp} 次重试")

if __name__ == "__main__":

    DEST_FOLDER       = "/media/sda5/cyn-workspace/UI-SPEC/results-spec"
    CODE_PATH         = "/media/sda5/cyn-workspace/UI-SPEC/my-app/src/App.js"
    WAIT_SELECTOR     = "#root"
    PORT              = 3000

    # 这里假设 utils.prompt 中定义了以下两条提示 (请根据实际文件调整)
    # spc_prompt：用于图片到 spec 的提示
    # code_prompt_img：用于从提取的 spec 生成代码的提示 (带 "{spec_input}")
    # code_prompt_spec：用于从已有 spec 生成代码的提示 (带 "{spec_input}")

    os.makedirs(DEST_FOLDER, exist_ok=True)
    SRC_IMAGES_FOLDER = '/media/sda5/cyn-workspace/UI-SPEC/test_img'
    # 如果要处理仅图片输入，解除下面一行注释：
    # batch_process_images(
    #     src_folder=SRC_IMAGES_FOLDER,
    #     code_path=CODE_PATH,
    #     port=PORT,
    #     wait_selector=WAIT_SELECTOR,
    #     dest_folder=DEST_FOLDER,
    #     spec_prompt=spec_prompt,
    #     code_prompt=code_prompt_web_v6
    # )
    # exit(0)
    # 如果要处理仅已有 spec 的 JSON，解除下面一行注释：
    # batch_process_json(
    #     spec_json_path="/media/sda5/cyn-workspace/UI-SPEC/all_spec_v2.json",
    #     code_path=CODE_PATH,
    #     port=PORT,
    #     wait_selector=WAIT_SELECTOR,
    #     dest_folder=DEST_FOLDER,
    #     code_prompt=code_prompt_web_v6
    # )
    # file_folder = "/media/sda5/cyn-workspace/UI-SPEC/final_tree_20250609_104605"
    # for file in os.listdir(file_folder):
    #     if not file.endswith(".json"):
    #         continue
    #     print(f"Processing file: {file}")
    #     process_single_json(
    #         spec_json_path=os.path.join(file_folder, file),
    #         code_path=CODE_PATH,
    #         save_file_name=file.split('.')[0],
    #         port=PORT,
    #         wait_selector=WAIT_SELECTOR,
    #         dest_folder=DEST_FOLDER,
    #         code_prompt=code_prompt_web_v6
    #     )
    process_single_json(
        spec_json_path="/media/sda5/cyn-workspace/UI-SPEC/final_tree_20250609_104605/market_dashboard_ui_design_636274253621471484.json",
        code_path=CODE_PATH,
        save_file_name="test",
        port=PORT,
        wait_selector=WAIT_SELECTOR,
        dest_folder=DEST_FOLDER,
        code_prompt=code_prompt_web_v6
    )
    exit(0)

    file_list = ["127538_1788004", "144813_2162659", "144826_2154395", "144813_2162659", "151901_2499351"]
    spec_json_path = "/media/sda5/cyn-workspace/UI-SPEC/all_spec_v2.json"
    spec_json = json.load(open(spec_json_path, 'r')) if isinstance(spec_json_path, str) else spec_json_path
    for spec in spec_json:
        file_name = spec.get("filename", "unknown_spec")
        if file_name not in file_list:
            continue  # 仅处理特定文件名
        screenshot_path = os.path.join(DEST_FOLDER, f"{file_name}.png")
        
        extracted_spec = spec.get("spec_res", "").strip()
        extracted_spec = extracted_spec['spec_res'] if isinstance(extracted_spec, dict) else extracted_spec
        with open(f"{DEST_FOLDER}/{file_name}.json", "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
        process_spec_with_edit(
            spec_json_path=f"{DEST_FOLDER}/{file_name}.json",
            code_path=CODE_PATH,
            save_file_name=f"spec_{file_name}",
            port=PORT,
            wait_selector=WAIT_SELECTOR,
            dest_folder=DEST_FOLDER,
            code_prompt=code_prompt_web_v8,
            gen_spec_tree=False,
        )

        process_spec_with_edit(
            spec_json_path=f"{DEST_FOLDER}/{file_name}.json",
            code_path=CODE_PATH,
            save_file_name=f"spec_{file_name}_tree",
            port=PORT,
            wait_selector=WAIT_SELECTOR,
            dest_folder=DEST_FOLDER,
            code_prompt=code_prompt_web_v8,
            gen_spec_tree=True,
        )

        process_spec_with_edit(
            spec_json_path=f"{DEST_FOLDER}/{file_name}.json",
            code_path=CODE_PATH,
            save_file_name=f"spec_{file_name}_v1",
            port=PORT,
            wait_selector=WAIT_SELECTOR,
            dest_folder=DEST_FOLDER,
            code_prompt=code_prompt_web_v8,
            gen_spec_tree=True,
            edit_prompt="如果spec树里有数据展示的组件，换一个不一样的"
        )
