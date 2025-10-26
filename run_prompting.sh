#!/bin/bash

# 激活虚拟环境（如有）
# source venv/bin/activate

# 设置参数
PROMPT_METHOD="direct_prompting"   # 可选：direct_prompting, text_augmented_prompting, revision_prompting, layout_marker_prompting
ORIG_OUTPUT_DIR="gpt4o_direct_prompting"
FILE_NAME="all"                             # 或指定文件名，例如："example.png"
SUBSET="testset_100"                        # 可选：testset_100 或 testset_full
TAKE_SCREENSHOT="--take_screenshot"         # 去掉就不截图
AUTO_INSERTION="--auto_insertion=False"     # True 或 False，仅 layout_marker_prompting 使用

# 运行脚本
python benchmark.py \
  --prompt_method $PROMPT_METHOD \
  --orig_output_dir $ORIG_OUTPUT_DIR \
  --file_name $FILE_NAME \
  $TAKE_SCREENSHOT \