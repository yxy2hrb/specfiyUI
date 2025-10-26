# 🧠 UI-SPEC 后端服务文档

## 📌 项目简介

本项目基于 Flask 搭建，是一个用于将 UI 截图或文本描述智能转化为 UI 设计规范（SPEC）和可运行代码的后端服务。该系统依赖 GPT 模型进行智能推理，支持 UI 区域提取、布局优化、组件识别、代码生成等多个子任务，最终目标是实现 UI 设计的自动化生成与优化。

---

## 📂 目录结构概览

```bash
.
├── app.py                    # 主应用入口，包含所有API路由
│   infer_llm.py      # 封装模型调用与推理逻辑
├── utils/
│   ├── gpt_api.py            # 封装 GPT 接口调用
│   ├── prompt.py             # 各种 prompt 模板
├── code_gen/
│   ├── gen_code.py           # 生成 React 代码
│   └── code_debug.py         # 自动运行并截图调试 React 应用
├── spec_editor/
│   └── edit_ui_spec_v2.py    # 编辑 UI 规范树
└── backend_results/
    └── image-results/        # 推理与渲染结果存储目录
```

---

## 🚀 快速启动

```bash
pip install -r requirements.txt
python app.py
# 服务默认运行在 http://0.0.0.0:55500
```

---

## 🌐 API 说明文档

### 1. `POST /api/image_to_spec`

> 上传图片，提取完整的 UI SPEC（结构化页面规范）

* **请求参数**

```json
{
  "image": "<base64编码图像>",
  "save_name": "my_dashboard"
}
```

* **返回示例**

```json
{
  "success": true,
  "data": {
    "spec": { ... }  // JSON格式的UI结构
  }
}
```

---

### 2. `POST /api/adjust_spec_layout`

> 根据区域的 BBox 大小自动优化布局描述字段

* **请求参数**

```json
{
  "spec": { ... }  // 原始 UI 规范
}
```

* **返回**

```json
{
  "success": true,
  "data": {
    "spec": { ... }  // 布局优化后的新规范
  }
}
```

---

### 3. `POST /api/text_to_spec`

> 将用户文本描述转换为 UI 规范

* **请求**

```json
{
  "text": "我需要一个销售数据仪表盘...",
  "save_name": "text_dash"
}
```

* **返回**

```json
{
  "success": true,
  "data": {
    "spec": { ... }
  }
}
```

---

### 4. `POST /api/edit_spec`

> 编辑现有 UI 规范（根据意图文本）

```json
{
  "text": "把第一个图表换成折线图",
  "spec": { ... },
  "save_name": "chart_edit"
}
```

---

### 5. `POST /api/combine_spec`

> 合并多个 SPEC 为一个整体页面结构

```json
{
  "spec_list": ["spec1结构", "spec2结构..."],
  "save_name": "combined_spec"
}
```

---

### 6. `POST /api/generate_code`

> 根据 UI 规范生成 React 页面代码，并返回截图

```json
{
  "spec": { ... },
  "save_name": "final_ui"
}
```

* **返回**

```json
{
  "code": "// React + AntD 代码",
  "render_image": "<base64截图>"
}
```

---

## 📚 Prompt 类型说明（由 GPT 使用）

| Prompt 名称                      | 功能描述                 |
| ------------------------------ | -------------------- |
| `spec_prompt_CYN`              | 从图片中提取完整 UI 结构规范     |
| `text_to_spec_prompt`          | 从文本转 UI 结构规范         |
| `adjust_layout_by_bbox_prompt` | 根据 BBox 自动优化布局字段     |
| `merge_prompt`                 | 合并多个 UI 规范描述         |
| `division_prompt_v2`           | 提取区域/组件信息结构          |
| `code_prompt_web_v8`           | 将 SPEC 转为前端 React 代码 |

---

## 🗂️ 结果存储路径

* 原图、推理结果、截图、生成代码：

  ```
  /media/sda5/cyn-workspace/UI-SPEC/backend_results/image-results/
  ```
