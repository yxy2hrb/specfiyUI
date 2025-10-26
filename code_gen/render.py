from playwright.sync_api import sync_playwright
import logging, sys, os
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("render.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def render_and_capture(
    url: str,
    screenshot_path: str,
    wait_selector: str = None
) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    with sync_playwright() as pw:
        # 这里换成 launch_persistent_context
        context = pw.firefox.launch_persistent_context(
            user_data_dir="tmp_data",   # 必须指定一个目录，用来存储 profile
            headless=True,
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            firefox_user_prefs={
                "font.default.x-unicode":        "sans-serif",
                "font.name.sans-serif.x-unicode":    "Microsoft YaHei",
                "font.name.serif.x-unicode":         "Microsoft YaHei",
                "font.name.monospace.x-unicode":     "Microsoft YaHei",
                "font.name.sans-serif.zh-CN":        "Microsoft YaHei",
                "font.name.serif.zh-CN":             "Microsoft YaHei",
                "font.name.monospace.zh-CN":         "Microsoft YaHei",
            }
        )
        page = context.pages[0]  # persistent context 会自动打开一个标签页

        page.on("pageerror", lambda exc: errors.append(f"[PAGE ERROR] {exc}"))

        try:
            page.goto(url, wait_until="networkidle")
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=5000)
            page.wait_for_timeout(3000)

            if errors:
                logging.error("捕获到前端错误：\n" + "\n".join(errors))
                return False, errors

            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)
            return True, []
        except Exception:
            logging.exception("渲染或截图过程出错：")
            return False, errors
        finally:
            context.close()

if __name__ == "__main__":
    ok, errs = render_and_capture("http://localhost:3001", r"D:\xdw_test\renderyahei.png", wait_selector="#root")
    if not ok:
        print("❌ 出错：", errs)
    else:
        print("✅ 成功截图")
