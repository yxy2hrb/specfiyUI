spec_prompt_structured = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整的信息，并给出尽可能还原的UI描述。
请根据我所提供的UI图片，从以下的信息维度全面解析UI中的内容，并尽可能详细地还原其设计细节。我将给你一个树状的json结构，请按照我提供的结构来进行UI设计稿的描述，你输出的内容应该是一段json格式的内容。
以下是一段json格式的参考，严格按照这个结构进行：
{
  "UI描述": {
    "整体描述": "",
    "功能简述": "",
    "产品场景": "",
    "目标用户": "",
    "核心功能": ""
  },
  "页面构成": {
    "区域划分": [
      {
        "区域名称": "",
        "区域简述": "",
        "包含组件": [
          {
            "组件类型": "",
            "承担的功能": "",
            "承载的信息": "",
            "组件的配色样式和布局": "",
            "组件所处的位置": "",
            "组件内的布局样式":""
          },
          {
            "组件类型": "",
            "承担的功能": "",
            "承载的信息": "",
            "组件的配色样式和布局": "",
            "组件所处的位置": "",
            "组件内的布局样式":""
          }
        ]
      },
      {
        "区域名称": "",
        "区域简述": "",
        "包含组件": [
          {
            "组件类型": "",
            "承担的功能": "",
            "承载的信息": "",
            "组件的配色样式和布局": "",
            "组件所处的位置": "",
            "组件内的布局样式":""
          },
          {
            "组件类型": "",
            "承担的功能": "",
            "承载的信息": "",
            "组件的配色样式和布局": "",
            "组件所处的位置": "",
            "组件内的布局样式":""
          }
        ]
      }
    ]
  },
  "视觉风格": {
    "整体调性": "",
    "色彩体系": "",
    "设计风格": ""
  }
}
** 请注意遵从以下要求：
**1. 区域和组件的拆分需要合理，具有整体性和模块化**
**2. 组件中的信息应以信息对象模型的形式完整再现，不要省略**
**3. 对于图表类型的组件需要读出图表中的具体数据**

"""

spec_to_structured_prompt = """
Your task: Generate the corresponding page structure tree based on the user input below. **Only** output content that strictly conforms to the JSON standard. **Do not** include any comments, explanatory text, or extra symbols.
Be sure to use double quotes (") to enclose all property names and string values; single quotes must not appear.
Requirements:
1. The generated structure tree must be valid JSON.
2. The structure tree fields must include: uiName, description, pageStructure, components:{text, style, layout, children}

```user input
{user input}
```

Response in JSON format:
```json

```
"""

"""
以下是优化后的提示（Prompt），以帮助模型更准确地根据页面描述生成符合要求的页面结构树：

````
你的任务：根据下方“页面描述”生成对应的页面结构树（JSON 格式）。

格式要求：
1. 输出必须是有效的 JSON，对象根节点无需额外说明。
2. JSON 对象需包含以下字段：
   - uiName：页面名称（字符串）
   - description：页面简要描述（字符串）
   - pageStructure：页面整体结构概述（字符串或数组，根据具体需求）
   - components：组件列表（数组），每个组件需包含以下子字段：
     • text：组件文本内容（字符串，如果无文本可留空或使用 null）
     • style：组件样式信息（对象，如颜色、字体、大小等）
     • layout：组件布局信息（对象，如宽度、高度、位置、边距等）
     • children：子组件列表（数组，若无子组件填写空数组）

使用示例：
```text
页面描述：
    这是一个登录页面，上方有一个标题“欢迎登录”，中间有两个输入框（用户名和密码），下方有一个“登录”按钮。
````

请根据上述描述直接输出结构树，例如：

```json
{
  "uiName": "登录页面",
  "description": "用户登录界面，包含标题、用户名输入框、密码输入框和登录按钮",
  "pageStructure": ["标题", "用户名输入框", "密码输入框", "登录按钮"],
  "components": [
    {
      "text": "欢迎登录",
      "style": { "fontSize": 24, "fontWeight": "bold", "color": "#333333" },
      "layout": { "width": "100%", "height": 50, "marginTop": 20, "textAlign": "center" },
      "children": []
    },
    {
      "text": "",
      "style": { "borderColor": "#cccccc", "borderRadius": 4 },
      "layout": { "width": "80%", "height": 40, "marginTop": 30, "alignSelf": "center" },
      "children": []
    },
    {
      "text": "",
      "style": { "borderColor": "#cccccc", "borderRadius": 4 },
      "layout": { "width": "80%", "height": 40, "marginTop": 10, "alignSelf": "center" },
      "children": []
    },
    {
      "text": "登录",
      "style": { "backgroundColor": "#0066ff", "color": "#ffffff", "borderRadius": 4 },
      "layout": { "width": "80%", "height": 45, "marginTop": 20, "alignSelf": "center" },
      "children": []
    }
  ]
}
```

现在输入用户提供的“页面描述”，请返回对应的 JSON 结构树：

```text
{user input}
```

```json
```

```
```

说明：

* 请务必严格按照 JSON 格式输出，不要包含多余注释或解释文字。
* 根据实际“页面描述”补充或省略不必要的字段，但组件必须包含 text、style、layout、children 四项。

```

上述提示示例可直接复制粘贴至使用场景中，供模型根据任意页面描述输出规范的 JSON 结构树。
```

"""

merge_prompt = """
请将以下多个页面结构树合并为一个完整的页面结构树。每个页面结构树都包含 uiName、description、pageStructure 和 components 字段。
请确保合并后的结构树仍然符合 JSON 格式，并且每个页面的结构和组件信息都被保留。
合并后的结构树应包含以下字段：
- uiName: 合并后的页面名称
- description: 合并后的页面描述
- pageStructure: 合并后的页面结构概述
- components: 合并后的组件列表，每个组件应包含 text、style、layout 和 children 字段。
请注意，合并时要确保组件的唯一性，避免重复，并且保持结构的清晰和一致性。
以下是需要合并的页面结构树列表：
{spec_list}
请输出合并后的 JSON 结构树：
```json
```
"""