import json
import re
from code_debug import iterative_debug
import os
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.prompt import code_prompt_v2
from utils.gpt_api import gpt_infer_no_image

# 用于保护多个线程写同一个 code_path 的冲突
write_lock = threading.Lock()

def process_file(
    fname: str,
    src_folder: str,
    code_path: str,
    port: int,
    wait_selector: str,
    dest_folder: str
):
    base_name = os.path.splitext(fname)[0]
    screenshot_path = os.path.join(dest_folder, f"{base_name}.png")

    if os.path.exists(screenshot_path):
        print(f"⏭️ {fname} 已存在截图，跳过")
        return

    spec_path = os.path.join(src_folder, fname)
    print(f"\n🔄 线程[{threading.current_thread().name}] 处理 {spec_path}")
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        spec = data.get("spec_res", "")
    except Exception as e:
        print(f"⚠️ 读取 {fname} 失败：{e}")
        return

    # 生成代码
    try:
        prompt = code_prompt_v2.replace('{spec_input}', spec)
        code = None
        for i in range(1, 4):
            res = gpt_infer_no_image(prompt)
            m = re.search(r'```jsx\n(.*?)\n```', res, re.DOTALL)
            if m:
                code = m.group(1).strip()
                print(f"✅ {fname} 第 {i} 次提取到代码")
                break
            else:
                print(f"⚠️ {fname} 第 {i} 次未提取到代码" + ("，重试" if i<3 else "，放弃"))

        # 保存 JSON
        os.makedirs(dest_folder, exist_ok=True)
        meta = {
            'image_path': screenshot_path,
            'extracted_spec': spec,
            'extracted_code': code
        }
        with open(os.path.join(dest_folder, f'{base_name}_origin_code.json'),
                  'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=4)

        # 并发安全写入 App.js
        with write_lock:
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code or "")
        print(f"✅ {fname} 代码写入 {code_path}")
    except Exception as e:
        print(f"⚠️ {fname} 生成/写入代码失败：{e}")
        return

    # 调试截图
    ok = iterative_debug(
        code_path, port, wait_selector,
        screenshot=screenshot_path,
        log_dir=dest_folder, image_path=dest_folder
    )
    if ok:
        print(f"✅ {fname} 调试并截图完成")
    else:
        print(f"❌ {fname} 调试失败，请查看日志")

def batch_process_specs(
    src_folder: str,
    code_port_pairs: list[tuple[str,int]],
    wait_selector: str,
    dest_folder: str
):
    if not os.path.isdir(src_folder):
        print(f"⚠️ 源文件夹不存在：{src_folder}")
        return
    os.makedirs(dest_folder, exist_ok=True)

    files = [f for f in os.listdir(src_folder) if f.lower().endswith(".json")]
    random.shuffle(files)

    n = len(code_port_pairs)
    # 并发数与 code_port 配对数保持一致
    with ThreadPoolExecutor(max_workers=n) as exe:
        futures = []
        for idx, fname in enumerate(files):
            code_path, port = code_port_pairs[idx % n]
            futures.append(
                exe.submit(
                    process_file,
                    fname, src_folder,
                    code_path, port,
                    wait_selector, dest_folder
                )
            )
        for fut in as_completed(futures):
            # 捕获异步异常
            try:
                fut.result()
            except Exception as e:
                print(f"❌ 处理任务出错：{e}")

if __name__ == "__main__":
    SRC = r"D:\xdw_test\myfolder\code-generation\data\all_spec"
    DEST = r"D:\xdw_test\myfolder\code-generation\data\sft_data_v3_0519"
    WAIT = "#root"

    # 四个 (code_path, port) 配对
    CODE_PORT_PAIRS = [
        (r"D:\xdw_test\code_generation_codebases\app_1\src\App.js", 3001),
        (r"D:\xdw_test\code_generation_codebases\app_2\src\App.js", 3002),
        (r"D:\xdw_test\code_generation_codebases\app_3\src\App.js", 3003),
    ]

    batch_process_specs(SRC, CODE_PORT_PAIRS, WAIT, DEST)
