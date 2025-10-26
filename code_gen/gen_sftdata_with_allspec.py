import json
import re
# import code_check.render
from code_debug import iterative_debug
import sys, os
import time
import random                        # ① 引入 random
from utils.prompt import base_spec_propmt, code_prompt_v2, spc_dsx_v2
from utils.gpt_api import gpt_infer_no_image

def batch_process_specs(
    src_folder: str,
    code_path: str,
    port: int,
    wait_selector: str,
    dest_folder: str
):
    """
    对 src_folder 中的所有文件：
      1. 调用 generate_code_single 生成代码并写入 code_path
      2. 调用 iterative_debug 进行渲染+调试，截图保存在 dest_folder
      如果目标文件对应截图已存在，则跳过该文件
    """
    if not os.path.isdir(src_folder):
        print(f"⚠️ 源文件夹不存在：{src_folder}")
        return

    os.makedirs(dest_folder, exist_ok=True)

    # ② 列出所有 .json 文件，打乱顺序
    all_files = [f for f in os.listdir(src_folder)
                 if f.lower().endswith(".json")]
    random.shuffle(all_files)

    for fname in all_files:
        base_name = os.path.splitext(fname)[0]
        screenshot_path = os.path.join(dest_folder, f"{base_name}.png")

        # 跳过已存在的截图
        if os.path.exists(screenshot_path):
            print(f"⏭️ {fname} 对应的截图已存在，跳过")
            continue

        spec_path = os.path.join(src_folder, fname)
        print(f"\n🔄 处理spec文件：{spec_path}")
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            extracted_spec = data.get("spec_res", "")
        except UnicodeDecodeError as e:
            print(f"⚠️ 无法用 utf-8 解码 {fname}：{e}")
            continue

        # 后面代码保持不变……
        # 1. 生成代码并写入 App.js
        try:
            formatted_code_prompt = code_prompt_v2.replace('{spec_input}', extracted_spec)
            extracted_code = None

            for attempt in range(1, 4):
                code_res = gpt_infer_no_image(formatted_code_prompt)
                match = re.search(r'```jsx\n(.*?)\n```', code_res, re.DOTALL)
                if match:
                    extracted_code = match.group(1).strip()
                    print(f'✅ 第 {attempt} 次尝试提取到有效代码')
                    break
                else:
                    print(
                        f'⚠️ 第 {attempt} 次未找到有效代码块，'
                        + ('准备重试' if attempt < 3 else '仍未找到')
                    )

            os.makedirs(dest_folder, exist_ok=True)
            json_path = os.path.join(dest_folder, f'{base_name}_origin_code.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'image_path': json_path,
                    'extracted_spec': extracted_spec,
                    'extracted_code': extracted_code
                }, f, ensure_ascii=False, indent=4)
            print(f'✅ 数据已保存到 {json_path}')

            with open(code_path, "w", encoding="utf-8") as f:
                f.write(extracted_code or "")
            print("✅ 生成并写入代码成功")
        except Exception as e:
            print(f"⚠️ 生成或写入代码失败：{e}")
            continue

        # 2. 调用 iterative_debug，生成专属截图
        success = iterative_debug(
            code_path,
            port,
            wait_selector,
            screenshot=screenshot_path,
            log_dir=dest_folder,
            image_path=dest_folder
        )
        if success:
            print(f"✅ {fname} 调试并截图完成：{screenshot_path}")
        else:
            print(f"❌ {fname} 调试未成功，请查看 json 和 GPT 建议")


        # # 3. 对spec进行衍生
        # try:
        #     newcode = derival_spec_single(img_path,spec,DEST_FOLDER)
        #     with open(code_path, "w", encoding="utf-8") as f:
        #         f.write(newcode)
        #     print("✅ 衍生新spec并写入代码成功")
        # except Exception as e:
        #     print(f"⚠️ 衍生后的spec生成或写入代码失败：{e}")
        #     continue
        # screenshot_path = os.path.join(dest_folder, f"derived_{base_name}.png")
        # # 2. 调用 iterative_debug，生成专属截图
        # success = iterative_debug(
        #     code_path,
        #     port,
        #     wait_selector,
        #     screenshot=screenshot_path
        # )

        # if success:
        #     print(f"✅ {fname} 衍生后调试并截图完成：{screenshot_path}")
        # else:
        #     print(f"❌ {fname} 衍生后调试未成功，请查看 json 和 GPT 建议")



if __name__ == "__main__":
    SRC_FOLDER   = r"D:\xdw_test\myfolder\code-generation\data\all_spec"
    # SRC_FOLDER = "/home/c50047709/cyn-workspace/images"
    DEST_FOLDER  = r"D:\xdw_test\myfolder\code-generation\data\sft_data_v3_0519_gpt"
    CODE_PATH    = r"D:\xdw_test\code-generation\code-generation\src\App.js"
    WAIT_SELECTOR = "#root"
    PORT         = 3001
    os.makedirs(DEST_FOLDER, exist_ok=True)
    batch_process_specs(
        SRC_FOLDER,
        CODE_PATH,
        PORT,
        WAIT_SELECTOR,
        DEST_FOLDER
    )
