from PIL import Image
import numpy as np
from PIL import ImageDraw

def soft_separation_lines(img, bbox=None, var_thresh=None, diff_thresh=None, diff_portion=None, sliding_window=None):
            """return separation lines (relative to whole image) in the area of interest specified by bbox (left, top, right, bottom). 
            Good at identifying blanks and boarders, but not explicit lines. 
            Assume the image is already rotated if necessary, all lines are in x direction.
            Boundary lines are included."""
            img_array = np.array(img.convert("L"))
            img_array = img_array if bbox is None else img_array[bbox[1]:bbox[3]+1, bbox[0]:bbox[2]+1]
            # import matplotlib.pyplot as plt
            # # show the image array
            # plt.imshow(img_array, cmap="gray")
            # plt.show()

            offset = 0 if bbox is None else bbox[1]
            lines = []
            for i in range(2*sliding_window, len(img_array) - sliding_window):
                upper = img_array[i-2*sliding_window:i-sliding_window]
                window = img_array[i-sliding_window:i]
                lower = img_array[i:i+sliding_window]
                is_blank = np.var(window) < var_thresh
                # content width is larger than 33% of the width
                is_boarder_top = np.var(upper) > var_thresh
                is_boarder_bottom = np.var(lower) > var_thresh
                # print(i, "is_blank", is_blank, "is_boarder_top", is_boarder_top, "is_boarder_bottom", is_boarder_bottom)
                if is_blank and (is_boarder_top or is_boarder_bottom):
                    line = (i + i - sliding_window) // 2
                    lines.append(line + offset)

            # print(sorted(lines))
            return sorted(lines)

def hard_separation_lines(img, bbox=None, var_thresh=None, diff_thresh=None, diff_portion=None):
    """return separation lines (relative to whole image) in the area of interest specified by bbox (left, top, right, bottom). 
    Good at identifying explicit lines (backgorund color change). 
    Assume the image is already rotated if necessary, all lines are in x direction
    Boundary lines are included."""
    img_array = np.array(img.convert("L"))
    # img.convert("L").show()
    img_array = img_array if bbox is None else img_array[bbox[1]:bbox[3]+1, bbox[0]:bbox[2]+1]
    offset = 0 if bbox is None else bbox[1]
    prev_row = None
    prev_row_idx = None
    lines = []

    # loop through the image array
    for i in range(len(img_array)):
        row = img_array[i]
        # if the row is too uniform, it's probably a line
        if np.var(img_array[i]) < var_thresh:
            # print("row", i, "var", np.var(img_array[i]))
            if prev_row is not None:
                # the portion of two rows differ more that diff_thresh is larger than diff_portion
                # print("prev_row", prev_row_idx, "diff", np.mean(np.abs(row - prev_row) > diff_thresh))
                if np.mean(np.abs(row - prev_row) > diff_thresh) > diff_portion:
                    lines.append(i + offset)
                    # print("line", i)
            prev_row = row
            prev_row_idx = i
    # print(sorted(lines))
    return lines

def draw_separation_lines(img, lines, color=(255, 0, 0), output_path="output_with_lines.jpg"):
    """
    在图像上画出分隔线，并保存。

    Args:
        img: 原始PIL图像对象。
        lines: 分隔线行号列表。
        color: 分隔线颜色 (默认红色)。
        output_path: 输出保存路径。
    """
    img_rgb = img.convert("RGB")
    draw = ImageDraw.Draw(img_rgb)
    width, height = img_rgb.size

    for y in lines:
        draw.line([(0, y), (width, y)], fill=color, width=1)

    img_rgb.save(output_path)
    print(f"保存可视化结果到: {output_path}")
# 假设你已经把上面的两个函数定义在本文件里，或者从模块导入：
# from your_module import soft_separation_lines, hard_separation_lines

# 1. 读取图像
img = Image.open("/media/sda5/cyn-workspace/UI-SPEC/test_img/image/test17.png")  # 一幅文本/表格页，水平分隔线在水平方向

# 2. 设定参数
# soft 方法：善于找空白行边界，比如段落间距或表格行间
soft_params = {
    "bbox": None,          # 整张图
    "var_thresh": 5.0,     # 小幅度噪声也能算“空白”
    "sliding_window": 3    # 向上/下各3行做对比
}

# hard 方法：善于找显式分隔线，如黑线、分割条
hard_params = {
    "bbox": None,
    "var_thresh": 2.0,     # 非常匀一的线条方差极低
    "diff_thresh": 15,     # 与上次候选线差异大于15灰度值
    "diff_portion": 0.4    # 差异像素占比超过40%
}

# 3. 执行检测
soft_lines = soft_separation_lines(
    img,
    bbox=soft_params["bbox"],
    var_thresh=soft_params["var_thresh"],
    diff_thresh=None,
    diff_portion=None,
    sliding_window=soft_params["sliding_window"]
)

hard_lines = hard_separation_lines(
    img,
    bbox=hard_params["bbox"],
    var_thresh=hard_params["var_thresh"],
    diff_thresh=hard_params["diff_thresh"],
    diff_portion=hard_params["diff_portion"]
)
# 绘制 soft 分隔线可视化
# draw_separation_lines(img, soft_lines, color=(255, 0, 0), output_path="soft_lines_output.jpg")

# # 绘制 hard 分隔线可视化
draw_separation_lines(img, hard_lines, color=(0, 0, 255), output_path="hard_lines_output.jpg")

# 如果想把两种线画在同一张图：
# all_lines = sorted(set(soft_lines + hard_lines))
# draw_separation_lines(img, all_lines, color=(0, 255, 0), output_path="all_lines_output.jpg")
# 4. 查看结果
print("Soft 分隔线行号：", soft_lines)
print("Hard 分隔线行号：", hard_lines)
