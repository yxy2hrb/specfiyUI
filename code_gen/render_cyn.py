from playwright.sync_api import sync_playwright
import logging
import sys
from typing import List, Tuple
import subprocess
import os
import time
import select
import signal
from pathlib import Path

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("render.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)



def run_recharts_transform(code_path: str, transformer_path: str) -> None:
    """
    在指定的 code_path 上原地执行 jscodeshift AST 转换，
    将从 'recharts' 导入的组件标签统一加上 isAnimationActive={false}。

    :param code_path: 支持 glob 的文件或目录路径，例如 "src/**/*.js"
    :param transformer_path: jscodeshift 转换脚本文件路径
    """
    # 确保 transformer 脚本存在
    transformer = Path(transformer_path)
    if not transformer.is_file():
        print(f"[Error] Transformer not found: {transformer}", file=sys.stderr)
        sys.exit(1)

    cmd = [
        "npx", "jscodeshift",
        "-t", str(transformer),
        code_path,
        "--extensions=js,jsx",
        "--parser=babel",
        "--verbose=2",        # 可选，输出更多调试信息
        "--ignore-pattern=**/node_modules/**"
    ]

    try:
        completed = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(completed.stdout)
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"[jscodeshift failed] Return code: {e.returncode}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(e.returncode)


def catch_react_compile_error(code_dir):
    env = os.environ.copy()
    env["PORT"] = "4022"

    proc = subprocess.Popen(
        ["npm", "start"],
        cwd=code_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        preexec_fn=os.setsid
    )

    start_time = time.time()
    timeout = 10
    is_failed = False
    error_msg = ""
    while True:
        # ⏱ 超时退出
        if time.time() - start_time > timeout:
            break

        # ⚠️ 使用 select 等待最多 0.1 秒读取一行
        rlist, _, _ = select.select([proc.stdout], [], [], 0.1)
        if rlist:
            line = proc.stdout.readline()
            if not line:
                break
            if "Failed" in line or "ERROR" in line:
                is_failed = True
            if is_failed:
                error_msg = f"{error_msg}\n{line}"


    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    proc.wait()
    return is_failed, error_msg



def render_and_capture(
    url: str,
    screenshot_path: str,
    code_dir: str,
    script_path: str,
    wait_selector: str = None
) -> Tuple[bool, List[str]]:
    """
    :param url: 页面地址
    :param screenshot_path: 截图保存路径
    :param wait_selector: 可选，渲染完成后才出现的元素选择器
    :return: (success, errors)
        success=True 则截图成功；False 则渲染或截图失败
        errors 为收集到的所有 console/pageerror 消息
    """
    code_path = f"{code_dir}/src/App.js"
    run_recharts_transform(code_path, script_path)
    errors: List[str] = []
    compile_err_flag, compile_err_msg = catch_react_compile_error(code_dir)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1000},
            device_scale_factor=1
        )
        page = ctx.new_page()
        
        # 收集 console 日志
        # page.on("console", lambda msg: errors.append(f"[{msg.type.upper()}] {msg.text}"))
        # 收集未捕获的页面错误
        page.on("pageerror", lambda exc: errors.append(f"[PAGE ERROR] {exc}"))

        try:
            page.goto(url, wait_until="networkidle")
            page.wait_for_load_state("networkidle")

            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=5000)


            page.wait_for_timeout(5000)
            page.screenshot(path=screenshot_path, full_page=True, animations='disabled')
            print("screenshot_path", screenshot_path)
            # 如果有错误信息，视为“渲染警告”而非脚本崩溃，依然返回截图，但标记 success=False
            if errors:
                if compile_err_flag:
                    errors.append(f"React编译错误：{compile_err_msg}")
                logging.error("捕获到前端错误：\n" + "\n".join(errors))
                return False, errors
            else:
                if compile_err_flag:
                    errors.append(f"React编译错误：{compile_err_msg}")
                    logging.error("捕获到错误：\n" + "\n".join(errors))
                    return False, errors
                else:
                    return True, []

        except Exception as e:
            # Python 层面的异常也算作失败
            logging.exception("渲染或截图过程出错：")
            if compile_err_flag:
                errors.append(f"React编译错误：{compile_err_msg}")
            # errors.append(f"[PYTHON EXCEPTION] {e}")
            return False, errors

        finally:
            browser.close()

if __name__ == "__main__":
    url = "http://localhost:41000"
    DEST_FOLDER = "/media/sda5/cyn-workspace/UI-SPEC/backend_results/image-results/gen_code_result"
    CODE_PATH = "/media/sda5/cyn-workspace/UI-SPEC/my-app/src/App.js"
    CODE_DIR = "/media/sda5/cyn-workspace/UI-SPEC/my-app"
    SCRIPT_PATH = "/media/sda5/cyn-workspace/UI-SPEC/my-app/src/transform-recharts-animation.js"
    PORT = 41000
    WAIT_SELECTOR = "#root"
    success, error_list = render_and_capture(url=url, screenshot_path="./test.png", code_dir=CODE_DIR, script_path=SCRIPT_PATH, wait_selector=WAIT_SELECTOR)

    if not success:
        print("❌ 渲染/截图过程中出现错误：")
        print(error_list)
    else:
        print("✅ 渲染并截图成功，无前端错误。")