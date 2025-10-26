from .render_cyn import render_and_capture
from utils.prompt import check_prompt
import re,sys,time
import logging,os,json
# from utils.qwen3_api import QwenClient
from utils.gpt_api import gpt_infer_no_image, gpt_infer
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

def read_code_file(path: str) -> str:
    """
    先以二进制读入，再尝试用 utf-8 解码，
    若遇到 UnicodeDecodeError 则忽略错误继续读完。
    """
    with open(path, 'rb') as f:
        raw = f.read()
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('utf-8', errors='ignore')

def analyze_render_errors(url: str, screenshot_path: str, wait_selector: str = None, code_path: str = None, errors: str = ""):
    """
    1. 调用 render_and_capture 渲染页面并截图
    2. 如果有错误，把错误日志 + 指定代码文件内容 拼成一个 prompt
    3. 调用 gpt_infer_no_image 进行分析，返回提取的修复代码（无错误时返回 None）
    """
    # 拼接错误信息
    error_text = "\n".join(errors)

    # 读取指定路径的代码（如果提供）
    code_text = ""
    if code_path:
        try:
            code_text = read_code_file(code_path)
            print(f"✅ 已读取 {code_path}，共 {len(code_text)} 字符")
        except Exception as e:
            print(f"⚠️ 无法读取代码文件 {code_path}：{e}")

    # 构造 prompt
    parts = [check_prompt, "\n\n=== 前端渲染错误 ===\n", error_text]
    if len(code_text)>100:
        parts.extend([f"\n\n=== 相关代码（来自 {code_path}）===\n", code_text])
        parts.extend(["\n\n不要出现使用注释来省略代码。请保证每次生成的代码都包含了完整的页面。\n\n"])
    else:
        print('没提取到需要debug的代码')
    final_prompt = "".join(parts)
    print('😊尝试debug的prompt总长度约为',len(final_prompt))
    # 调用 GPT 推理
    analysis = gpt_infer_no_image(final_prompt, model='gpt-5')

    # 提取代码块
    match = re.search(r'```jsx\n(.*?)\n```', analysis, re.DOTALL)
    if match:
        return match.group(1).strip()
    print("⚠️ 未从 GPT 响应中提取到代码块。")
    return None


def iterative_debug(
    code_path: str,
    port: int,
    code_dir: str,
    script_path: str,
    wait_selector: str = "#root",
    screenshot: str = "1.png",
    max_attempts: int = 3,
    log_dir: str = './gen_code_result_0509',
    image_path = './gen_code_result_0509',
    useQwen=False
) -> bool:
    """
    循环最多 max_attempts 次：
    1. 记录当前代码、渲染错误
    2. 调用 analyze_render_errors 获取修复代码
    3. 应用修复并记录

    参数:
      - code_path: 代码文件路径
      - port: 本地服务器端口
      - wait_selector: 渲染等待的 CSS 选择器
      - screenshot: 截图保存路径
      - max_attempts: 最大调试次数
      - log_dir: 日志保存目录，若为 None 则使用 code_path 所在目录

    返回:
      - 渲染成功返回 True，否则 False
    """
    url = f"http://localhost:{port}"
    # 用于记录所有尝试
    debug_log = {
        'code_path': code_path,
        'url': url,
        'attempts': []
    }

    # 迭代尝试
    for attempt in range(1, max_attempts + 1):
        time.sleep(2)
        print(f"=== 第 {attempt}/{max_attempts} 次调试 ===")
        # 读取当前代码
        try:
            with open(code_path, 'r', encoding='utf-8') as f:
                current_code = f.read()
        except Exception as e:
            logging.error(f"尝试 {attempt} 读取代码失败：{e}")
            current_code = ''

        # 尝试渲染并捕获错误
        success, errors = render_and_capture(url=url, screenshot_path=screenshot, code_dir=code_dir, script_path=script_path, wait_selector=wait_selector)
        if success:
            print("✅ 页面渲染成功，调试结束。")
            debug_log['result'] = 'success'
            _save_debug_log(code_path, debug_log, log_dir)
            return True, None

        # 渲染失败，记录错误并调用 GPT 修复
        print(f"❌ 渲染失败，捕获到错误: {errors}")
        screenshot = Path(screenshot)
        
        # split stem and suffix
        stem = screenshot.stem        # "1"
        suffix = screenshot.suffix    # ".png"

        # construct new filename, e.g. "1-debug.png"
        debug_screenshot = screenshot.parent / f"{stem}-debug{suffix}"
        fixed_code = analyze_render_errors(url, debug_screenshot, wait_selector, code_path,errors=errors)

        # 记录本次尝试信息
        debug_log['attempts'].append({
            'attempt': attempt,
            'errors': errors,
            'original_code': current_code,
            'fixed_code': fixed_code
        })

        # 记录修复代码到日志
        logging.info(f"=== 尝试 {attempt} GPT 修复代码 ===\n{fixed_code}")
        # 将修复后的代码写回
        try:
            with open(code_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code or '')
        except Exception as e:
            print(f"⚠️ 写入修复代码失败：{e}")
            debug_log['result'] = 'error_writing'
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            json_path = os.path.join(log_dir, f'{image_name}_debuged_code.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(debug_log, f, ensure_ascii=False, indent=4)
            return False, fixed_code
    try:
        with open(code_path, 'r', encoding='utf-8') as f:
            current_code = f.read()
    except Exception as e:
            logging.error(f"尝试 {attempt} 读取代码失败：{e}")
            current_code = ''

    # 尝试渲染并捕获错误
    success, errors = render_and_capture(url=url, screenshot_path=screenshot, code_dir=code_dir, script_path=script_path, wait_selector=wait_selector)
    if success:
        
        print("✅ 页面渲染成功，调试结束。")
        debug_log['result'] = 'success'
        _save_debug_log(code_path, debug_log, log_dir)
        return True, fixed_code
    # 达到最大次数仍未成功
    print("❌ 达到最大调试次数，仍未成功渲染。")
    debug_log['result'] = 'failed'
    _save_debug_log(screenshot, debug_log, log_dir)
    return False


def _save_debug_log(code_path: str, log_data: dict, log_dir: str = None):
    """
    将日志保存为 JSON 文件。
    若指定 log_dir，则保存到该目录，否则保存到 code_path 所在目录。
    文件命名为 <basename>_debug.json。
    """
    # 确定目录
    if log_dir:
        dirpath = log_dir
    else:
        dirpath = os.path.dirname(code_path)
    os.makedirs(dirpath, exist_ok=True)

    base = os.path.splitext(os.path.basename(code_path))[0]
    json_path = os.path.join(dirpath, f"{base}_debug.json")

    try:
        with open(json_path, 'w', encoding='utf-8') as jf:
            json.dump(log_data, jf, ensure_ascii=False, indent=4)
        print(f"✅ 调试日志已保存到 {json_path}")
    except Exception as e:
        print(f"⚠️ 无法保存调试日志：{e}")