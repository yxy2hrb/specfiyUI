layout_tree_prompt = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整的信息，并给出尽可能还原的UI描述。
请根据我所提供的UI图片，从以下的信息维度全面解析UI中的内容，并尽可能详细地还原其设计细节。我将给你一个树状的json结构，请按照我提供的结构来进行UI设计稿的描述。
其中包括三个部分：
1.UI描述：提供整体的页面信息，包括整体描述、功能简述、产品场景、目标用户、核心功能
2.页面构成：按照页面-区域-组件三个层级，每个层级包括一些详细信息。
3.视觉风格：包括整体调性、色彩体系、设计风格。其中，色彩体系对于各个颜色的描述要采用一些修饰词尽量准确描述颜色。
** 请注意遵从以下要求：
**1. 区域和组件的拆分需要合理，具有整体性和模块化**
**2. 组件中的信息应以信息对象模型的形式完整再现，不要省略**
**3. 对于图表类型的组件需要读出图表中的具体数据**
以下是一段json格式的参考，严格按照这个结构进行输出：
```json
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
        "区域所在页面位置":"",
        "区域内各组件布局":"",
        "包含组件": [
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
```
"""

color_tree_prompt = """
你是一位经验丰富的UI设计师，擅长为UI选择配色。
我会为你提供一段描述UI的JSON格式的文本，以及提供给UI的配色方案。
请根据这一段UI的描述内容，使用提供的配色方案来重新描述UI。
注意以下要求：
**1. 不要改变描述UI的JSON文本中的任何其他内容，也不要省略，只能且必须修改所有描述颜色的文本。**
**2. 对于原来描述中的颜色，请使用所提供的颜色进行替换（必须注明具体的颜色色号）。替换用的颜色必须是配色方案中包括的颜色以及灰色（深浅灰色根据页面调整）。**
**3. 不是所有提及的颜色都要用到。**
**4. 请直接生成JSON格式的新的UI描述，此外不要生成任何内容。**
输出采用以下格式：
```json
<新的UI描述>
```
"""

comp_derive_prompt_v0 = """
你是一位富有创意且注重细节的UI设计师，擅长基于功能需求对现有UI组件进行创新性重构。我将提供一个UI组件的文本描述作为输入，请你据此生成五种不同的UI组件变换方案。
**Input: UI组件的文本描述**
{UI组件的文本描述}
**任务要求如下：**
1. **功能优先**：在变换过程中，必须确保组件所承担的功能和承载的信息完全不发生任何损失。
2. **多样化设计**：每种方案应尽可能在视觉表现和交互形式上与原组件有显著差异。如果需要重构成图表组件，你需要使用知识库中的图表类型，并选择合理的图表类型。
3. **独立描述**：请直接描述变换后的组件内容，描述格式与输入格式相同，**不要提及或对比原始组件**。
4. **数量要求**：请输出**五个不同的设计方案**，且五个方案之间不要雷同。
5. **格式统一**：变换后的方案使用统一的JSON结构格式输出，具体格式如下：
```json
[
  {
    "组件类型": "组件名称",
    "承担的功能": "组件的核心功能描述",
    "承载的信息": "组件展示的具体信息项列表或描述",
    "组件所处的位置": "组件在页面中的相对位置（如顶部、中部、底部等）",
    "组件内的布局样式": "组件内部内容的排列方式和结构描述"
  },
]
```
注意：
1. json的key不能翻译成英文
2. 输出的json必须被```json  ```所包裹，使得输出能够被正则表达式pattern = r"```json\s*([\s\S]*?)\s*```"正确解析。
"""

comp_derive_prompt = """
你是一位富有创意且注重细节的UI设计师，擅长基于功能需求对现有UI组件进行创新性重构。我将提供一个UI组件的文本描述作为输入，请你据此生成五种不同的UI组件变换方案。
**Input: UI组件的文本描述**
{UI组件的文本描述}
**任务要求如下：**
1. **功能优先**：在变换过程中，必须确保组件所承担的功能和承载的信息完全不发生任何损失。
2. **对于组件详细说明**:需要结合该组件的类型详细描述该组件的外观(不少于4句话)。
3. **多样化设计**：每种方案应尽可能在视觉表现和交互形式上与原组件有显著差异。如果需要重构成图表组件，你需要使用知识库中的图表类型，并选择合理的图表类型。
4. **独立描述**：请直接描述变换后的组件内容，描述格式与输入格式相同，**不要提及或对比原始组件**。
5. **数量要求**：请输出**五个不同的设计方案**，且五个方案之间不要雷同。
6. **格式统一**：变换后的方案使用统一的JSON结构格式输出，具体格式如下：
```json
[
  {
    "组件类型": "组件名称",
    "组件详细说明": "组件类型详细说明",
    "承担的功能": "组件的核心功能描述",
    "承载的信息": "组件展示的具体信息项列表或描述",
    "组件所处的位置": "组件相对于区域所在的位置，与其他组件的位置关系，并给出组件的占比。",
    "组件内的布局样式": "应当清晰写出组件内的排版布局，横向、纵向或者z字形等排版样式，并清晰描述组件内各元素的布局。"
  },
]
```

注意：
1. json的key不能翻译成英文
2. 输出的json必须被字符```json和字符```所包裹！！使得输出能够被正则表达式pattern = r"```json\s*([\s\S]*?)\s*```"正确解析
3. 你必须不能遗漏输出json最后的```

"""

# 6.24 YJX版本
comp_derive_prompt_YJX = """
你是一位经验丰富的UI设计师，具有创造力和发散思维，擅长从功能和和需求角度出发来对现有的组件进行创意衍生。
具体来说，你需要根据我提供的一段UI组件的描述进行思维发散，在保证功能和需求不变的前提下写出5种不同的新的组件描述。
你需要按照以下要求执行该任务：
step1.充分理解原组件的功能和使用场景，并保证原组件的信息没有缺失。
step2.考虑多种组件衍生的方法，来生成新的组件描述方案
step3.检查衍生后的组件描述的信息完整性、可实现性与合理性，不要损失原本UI承载的信息，保证新的页面描述是能够被前端工程师开发出来的，还要检查新的UI描述是否合理地呈现了原先的信息。
在完成以上任务时，你需要遵循以下要求
1.保持功能和信息的一致：你需要保持新的UI组件描述与原UI组件描述在功能和承载信息上一致，不要缺失或省略。
2.保证多样化：你生成的新的页面描述要有较大差异，方案之间不要雷同，且至少生成五个相互不同的方案。
3.以前端代码实现为目标：你需要补充任何前端工程师采用React框架，使用Ant Design组件库和Recharts图表库还原出页面可能需要的信息。
4.输出格式要求：你需要按照我给你的任务步骤一步步执行，但输出内容只需要五段json格式的新UI描述，以下是输出格式的示例以及各个字段的要求：
{ 
  "组件编号": "需要对区域和组件进行编号，规则是区域为1、2、3以此类推，组件为1.1、1.2以此类推。",
  "组件类型": "按照antdesign中存在的组件类型进行描述。",
  "承担的功能": "从页面整体出发，描述该组件的具体功能。",
  "承载的信息": "组件中的信息应以信息对象模型的形式完整再现。对于表格，应写出表格共计多少行，并提取表头和表体中的每一项。对于图表，应该给出有几个数据条目，并提取每个条目，以及条目对应的数据。不要省略要求中的任何信息",
  "组件的详细描述": "从方便代码实现的角度详细描述组件的外观，不少于三句话",
  "组件的配色样式": "仅使用文本描述组件中各个部分使用的颜色（不要出现色号）",
  "组件所处的位置": "组件相对于区域所在的位置，与其他组件的位置关系，并给出组件的占比。",
  "组件内的布局样式":"应当清晰写出组件内的排版布局，横向、纵向或者z字形等排版样式，并清晰描述组件内各元素的布局。"
}
"""

comp_derive_prompt_v2 = """
你是一位富有创意且注重细节的UI设计师，擅长基于功能需求对现有UI组件进行创新性重构。我将提供一个UI组件的文本描述作为输入，请你据此生成五种不同的UI组件变换方案。
**Input: UI组件的文本描述**
{UI组件的文本描述}

你需要按照以下要求执行该任务：
step1.充分理解原组件的功能和使用场景，并保证原组件的信息没有缺失。
step2.考虑多种组件衍生的方法，来生成新的组件描述方案
step3.检查衍生后的组件描述的信息完整性、可实现性与合理性，不要损失原本UI承载的信息，保证新的页面描述是能够被前端工程师开发出来的，还要检查新的UI描述是否合理地呈现了原先的信息。

在完成以上任务时，你需要遵循以下要求
1.保持功能和信息的一致：你需要保持新的UI组件描述与原UI组件描述在功能和承载信息上一致，不要缺失或省略。
2.保证多样化：你生成的新的页面描述要有较大差异，方案之间不要雷同，且至少生成五个相互不同的方案。
3.以前端代码实现为目标：你需要补充任何前端工程师采用React框架，使用Ant Design组件库和Recharts图表库还原出页面可能需要的信息。
4.输出格式要求：你需要按照我给你的任务步骤一步步执行，但输出内容只需要五段json格式的新UI描述，以下是输出格式的示例以及各个字段的要求：
```json
[
  { 
    "组件类型": "需要尽量贴近ant design组件库的组件名称",
    "组件详细说明": "需要结合该组件类型详细描述该组件的外观(不少于4句话)",
    "承担的功能": "从整体出发，描述该组件的具体功能。",
    "承载的信息": "组件中的信息应以信息对象模型的形式完整再现。对于表格，应写出表格共计多少行，并提取表头和表体中的每一项。对于图表，应该给出有几个数据条目，并提取每个条目，以及条目对应的数据。不要省略要求中的任何信息",
    "组件所处的位置": "组件相对于区域所在的位置，与其他组件的位置关系，并给出组件的占比。",
    "组件内的布局样式":"应当清晰写出组件内的排版布局，横向、纵向或者z字形等排版样式，并清晰描述组件内各元素的布局。"
  }
]
```
注意：
1. json的key不能翻译成英文
2. 输出的json必须被```json  ```所包裹，使得输出能够被正则表达式pattern = r"```json\s*([\s\S]*?)\s*```"正确解析。
"""

division_prompt_v0= """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整信息，并给出尽可能还原的UI描述。
我会向你提供一张UI中的某个区域的图片，你的任务是从以下信息维度全面解析UI中的内容，并尽可能详细地还原其设计细节。
你给出的UI描述应包括以下两个部分：
1.区域名称：按照区域所承担的功能为这个区域命名。
2.包含组件：描述区域内所包含的全部组件，以及各个组件的详细信息，包括组件类型、承担的功能、承载的信息、组件所处的位置、组件内的布局。
** 请注意遵从以下要求：
**1. 对于组件类型，需要尽量贴近ant design组件库的组件名称**
**2. 组件中的信息应以信息对象模型的形式完整复述，不要省略任何信息。**
**3. 对于表格组件，不可以只描述表头却省略了表项，应该完整描述表格中每一项的信息。**
**4. 对于图表类型的组件需要读出图表中的具体数据。**
**5. 对于组件所处的位置，应尽可能精确描述，如在区域的相对什么位置，相对其它组件的位置，可以给出近似的比例数据描述。**
**6. 对于组件内的布局样式，应尽可能清楚描述，按照从上至下的顺序，逐行描述组件内的元素布局情况。**
以下是一段json格式的参考，严格按照这个结构进行输出：
**输出模板**
```json
{ 
  "区域名称": "",
  "包含组件": [
    { 
      "组件类型": "",
      "承担的功能": "",
      "承载的信息": "",
      "组件所处的位置": "",
      "组件内的布局样式":""
    }
  ]
}
```
注意：
1. 输出json的key严格按照模板进行输出，不能翻译成英文，不能篡改key的名称，例如组件类型不能改成组件型

"""

division_prompt = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整信息，并给出尽可能还原的UI描述。
我会向你提供一张UI中的某个区域的图片，你的任务是从以下信息维度全面解析UI中的内容，并尽可能详细地还原其设计细节。
你给出的UI描述应包括以下两个部分：
1.区域名称：按照区域所承担的功能为这个区域命名。
2.包含组件：描述区域内所包含的全部组件，以及各个组件的详细信息，包括组件类型、组件类型详细说明、承担的功能、承载的信息、组件所处的位置、组件内的布局。
** 请注意遵从以下要求：
**1. 对于组件类型，需要尽量贴近ant design组件库的组件名称**
**2. 对于组件详细说明，需要结合该组件类型详细描述该组件的外观(不少于3句话)**
**3. 组件中的信息应以信息对象模型的形式完整复述，不要省略任何信息。**
**4. 对于表格组件，不可以只描述表头却省略了表项，应该完整描述表格中每一项的信息。**
**5. 对于图表类型的组件需要读出图表中的具体数据。**
**6. 对于组件所处的位置，应尽可能精确描述，如在区域的相对什么位置，相对其它组件的位置，可以给出近似的比例数据描述。**
**7. 对于组件内的布局样式，应尽可能清楚描述，按照从上至下的顺序，逐行描述组件内的元素布局情况。**
以下是一段json格式的参考，严格按照这个结构进行输出：
**输出模板**
```json
{ 
  "区域名称": "",
  "包含组件": [
    { 
      "组件类型": "",
      "组件详细说明": "",
      "承担的功能": "",
      "承载的信息": "",
      "组件所处的位置": "",
      "组件内的布局样式":""
    }
  ]
}
```
注意：
1. 输出json的key严格按照模板进行输出，不能翻译成英文

"""


# 6.24 CWK YJX 合并版本
division_prompt_v2 = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整信息，并给出尽可能还原的UI描述。
我会向你提供一张UI中的某个区域的图片，你的任务是从以下信息维度全面解析UI中的内容，并尽可能详细地还原其设计细节。
你给出的UI描述应包括以下两个部分：
1.区域名称：按照区域所承担的功能为这个区域命名。
2.包含组件：描述区域内所包含的全部组件，以及各个组件的详细信息，包括组件类型、组件类型详细说明、承担的功能、承载的信息、组件所处的位置、组件内的布局。

以下是一段json格式的参考，严格按照这个结构进行输出：
**输出模板**
```json
{ 
  "区域名称": "",
  "包含组件": [
    { 
      "组件类型": "需要尽量贴近ant design组件库的组件名称",
      "组件详细说明": "需要结合该组件类型详细描述该组件的外观(不少于4句话)",
      "承担的功能": "从整体出发，描述该组件的具体功能。",
      "承载的信息": "组件中的信息应以信息对象模型的形式完整再现。对于表格，应写出表格共计多少行，并提取表头和表体中的每一项。对于图表，应该给出有几个数据条目，并提取每个条目，以及条目对应的数据。不要省略要求中的任何信息",
      "组件所处的位置": "组件相对于区域所在的位置，与其他组件的位置关系，并给出组件的占比。",
      "组件内的布局样式":"应当清晰写出组件内的排版布局，横向、纵向或者z字形等排版样式，并清晰描述组件内各元素的布局。"
    }
  ]
}
```
** 请注意遵从以下要求：
**1. json示例中提出了各个部分提取的详细要求，请严格遵守各部分对应的要求进行，不要省略或编造。
**2. 描述的信息需要能够帮助前端工程师采用React框架，使用Ant Design组件库和Recharts图表库还原出页面
**3. 输出json的key严格按照模板进行输出，不能翻译成英文
"""


# 6.24 YJX版本
division_prompt_YJX = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整的信息，并给出尽可能还原的UI描述。
请根据我所提供的UI图片，从以下的信息维度全面解析UI中的内容，并尽可能详细地还原其设计细节。我将给你一个树状的json结构，请按照我提供的结构来进行UI设计稿的描述。
其中包括三个部分：
1.UI描述：提供整体的页面信息，包括整体描述、功能简述、产品场景、目标用户、核心功能
2.页面构成：按照页面-区域-组件三个层级，每个层级包括一些详细信息。
3.视觉风格：包括整体调性、色彩体系、设计风格。其中，色彩体系对于各个颜色的描述要采用一些修饰词尽量准确描述颜色。
以下是一段json格式的参考，严格按照这个结构进行输出：
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
        "区域编号": "需要对区域和组件进行编号，规则是区域为1、2、3以此类推，组件为1.1、1.2以此类推。",
        "区域名称": "",
        "区域所在页面位置":"应当清晰描述区域所在页面的相对位置，以及与其他区域的对齐关系，区域在占整个页面的比例",
        "区域内各组件布局":"应当清晰描述区域内各组件的排版布局，各个组件之间高度宽度的对齐关系，间距，比例大小等信息",
        "包含组件": [
          { 
            "组件编号": "需要对区域和组件进行编号，规则是区域为1、2、3以此类推，组件为1.1、1.2以此类推。",
            "组件类型": "按照antdesign中存在的组件类型进行描述。",
            "承担的功能": "从页面整体出发，描述该组件的具体功能。",
            "承载的信息": "组件中的信息应以信息对象模型的形式完整再现。对于表格，应写出表格共计多少行，并提取表头和表体中的每一项。对于图表，应该给出有几个数据条目，并提取每个条目，以及条目对应的数据。不要省略要求中的任何信息",
            "组件的配色样式": "仅使用文本描述组件中各个部分使用的颜色（不要出现色号）",
            "组件所处的位置": "组件相对于区域所在的位置，与其他组件的位置关系，并给出组件的占比。",
            "组件内的布局样式":"应当清晰写出组件内的排版布局，横向、纵向或者z字形等排版样式，并清晰描述组件内各元素的布局。"
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
**1. 区域和组件的拆分需要合理，具有整体性和模块化。页面主体部分的区域应当按照横向楼层的概念进行划分。**
**2. json示例中提出了各个部分提取的详细要求，请严格遵守各部分对应的要求进行，不要省略或编造。
**3. 描述的信息需要能够帮助前端工程师采用React框架，使用Ant Design组件库和Recharts图表库还原出页面
"""

spec_prompt_CYN = """
You are an experienced UI designer, skilled at accurately extracting comprehensive information from UI screenshots and providing detailed, faithful UI descriptions.

Based on the UI image I provide, please analyze its content thoroughly across the following dimensions and reconstruct the design details as accurately as possible. I will give you a tree-structured JSON format — please describe the UI according to this structure.

The structure includes three main sections:

UI Description: Provide overall page information, including general overview, brief functionality summary, product context, target users, and core features.

Page Structure: Follow a hierarchical structure of Page → Section → Component. Each level should include detailed information.

Visual Style: Include overall tone, color system, and design style. For the color system, please describe each color with descriptive adjectives to ensure accurate depiction.
Constraints:
1. Responses must be in English.
2. The keys in the output JSON must match the reference structure below.
Here is a reference JSON format to follow strictly:
```json
{
  "UIDescription": {
    "OverallDescription": "A brief overview of the page's design style and overall visual layout characteristics, e.g., clean and modern style with a well-structured layout centered around card-based modules.",
    "FunctionSummary": "A summary of the main functional features implemented on the page, such as displaying product information, supporting filter and search, displaying statistical charts, etc.",
    "ProductScenario": "Explanation of the business or usage scenario this page is designed for, such as e-commerce admin dashboard or SaaS data analytics platform.",
    "TargetUsers": "Clearly defines the user group the page is intended for, such as operations staff, data analysts, general consumers.",
    "CoreFunctions": "A focused list of essential primary functions on the page that support key business needs."
  },
  "PageStructure": {
    "SectionDivision": [
      {
        "SectionID": "Should be uniquely identified, e.g., 1, 2, 3.",
        "SectionName": "Concise naming, e.g., Top Navigation Bar, Sidebar, Main Content Area.",
        "Location": "Clearly describes the section’s relative position on the page, its relation to other sections, and the proportion it occupies (e.g., top section spans 100% width of the page, occupies 10% of the page height).",
        "BBox": "Boundary box coordinates of the section, in the format: x1, y1, x2, y2 (top-left and bottom-right coordinates).",
        "LayoutStyleWithinSection": "Detailed description of how components are arranged within the section (e.g., horizontal layout, vertical layout, grid layout), alignment style, spacing ratios, etc.",
        "ContainedComponents": [
          {
            "ComponentID": "Use the pattern: section ID + component order, e.g., 1.1, 1.2, 2.1.",
            "ComponentType": "Strictly use Ant Design component names (e.g., Button, Table, Form, Tabs, Card, etc.).",
            "Functionality": "Describe the specific function of this component from the perspective of the page’s features, e.g., 'input for filter criteria', 'data display', etc.",
            "InformationCarried": "Describe the information within the component based on an object model. For tables, list: total rows, header fields, and data fields per row. For charts, list: total data items, each item’s name and corresponding value. The information should be complete and not omitted.",
            "ComponentColorStyle": "Describe the color of different parts of the component, e.g., button with dark background and white text, light gray border.",
            "ComponentPosition": "Describe the component’s relative position within the section (e.g., aligned left, right, top, bottom, center), its relation to adjacent components, and space occupancy.",
            "ComponentLayoutStyle": "Explain how elements inside the component are arranged (e.g., text vertically centered in button, chart arranged vertically, table as vertically scrollable list), and describe size ratios, spacing, and alignment of each element."
          }
        ]
      }
    ]
  },
  "VisualStyle": {
    "OverallTone": "E.g., professional, tech-savvy, light and friendly, steady, etc.",
    "ColorScheme": "Main color range used, e.g., deep blue and bright blue as primary colors, with light gray as background, and orange for highlights.",
    "DesignStyle": "E.g., minimalistic, skeuomorphic, flat design, card-style layout, etc."
  }
}

```
"""

adjust_layout_by_bbox_prompt = """
你是一位资深的UI设计专家，擅长根据页面区域的大小关系，优化页面布局描述，提升设计合理性与可还原性。

我将向你提供一段 UI 页面规范（JSON 格式），每个区域都包含一个 `BBox` 字段（格式为 "x1,y1,x2,y2"）。请你基于以下规则，重新生成 `区域内布局样式` 和"组件内的布局样式"字段的描述，并输出一个优化后的新的 UI 规范。

**你的任务目标如下：**

1. **理解区域大小：** 根据每个区域的 `BBox`（左上角、右下角坐标），推断区域的长宽、所占页面比例；
2. **优化布局描述：** 重新编写 `区域内布局样式` 和"组件内的布局样式"字段，使其更合理地描述组件排列方式（如：横向、纵向、网格、瀑布流等），说明组件间大小/对齐/间距关系；
3. **保持其他字段不变：** 除了 `区域内布局样式`和"组件内的布局样式"，其他信息如组件列表、颜色、位置说明等**保持原样不动**；
4. **语言要求：** 使用清晰、简洁、工程化的中文描述风格，确保前端开发人员能依据该描述进行还原；
5. **输出格式：** 只输出优化后的完整 JSON 规范，**格式与输入保持一致**。


**用户输入：**
{spec_input}

**输出格式：**
```json
以下是一段json格式的参考，严格按照这个结构进行输出：
{
  "UI描述": {
    "整体描述": "简要概述该页面的设计风格和整体视觉布局特点，例如：简洁现代风，布局规整，以卡片为核心模块。",
    "功能简述": "归纳页面实现的主要功能点，例如：展示产品信息、支持筛选搜索、展示统计图表等。",
    "产品场景": "说明该页面所处的业务场景或使用场景，例如：电商后台管理、SaaS数据分析平台。",
    "目标用户": "明确页面面向的用户群体，例如：运营人员、数据分析师、普通消费者。",
    "核心功能": "重点列出页面不可或缺的主要功能，聚焦于页面支撑的关键业务需求。"
  },
  "页面构成": {
    "区域划分": [
      {
        "区域编号": "应唯一标识，例如：1、2、3。",
        "区域名称": "简洁命名，例如：顶部导航栏、侧边栏、主内容区。",
        "所处的位置": "明确描述区域在整个页面的相对位置、与其他区域的关系、所占比例（例如：顶部区域横跨页面100%宽度，占页面高度10%）。",
        "BBox": "区域的边界框坐标，格式为：x1, y1, x2, y2（左上角和右下角坐标）。",
        "区域内布局样式": "详细描述区域内各组件的排列方式（如：横向排列、纵向排列、网格排列等）、对齐方式、间距比例等。",
        "包含组件": [
          {
            "组件编号": "规则为区域编号+组件顺序，例如：1.1、1.2、2.1。",
            "组件类型": "严格使用Ant Design组件名称（例如：Button、Table、Form、Tabs、Card等）。",
            "承担的功能": "从页面功能出发，描述该组件承担的具体功能点，例如：‘筛选条件输入’、‘数据展示’等。",
            "承载的信息": "以信息对象模型描述组件内包含的信息。若为表格，请列出：总行数、表头字段、每行的字段信息。若为图表，请列出：总数据条数、每条数据的名称及对应数值等。信息应完整、不可省略。",
            "组件的配色样式": "文本描述组件中不同部分的颜色，例如：按钮为深色背景搭配白色文字，边框为浅灰色。",
            "所处的位置": "描述组件在所在区域内的相对位置（例如：居左、居右、顶部、底部、中间），以及与相邻组件的关系及占比。",
            "组件内的布局样式": "说明组件内的元素排列方式（例如：按钮文本垂直居中，图表纵向排列，表格为纵向滚动列表），并描述各元素的大小比例、间距、对齐等。"
          }
        ]
      }
    ]
  },
  "视觉风格": {
    "整体调性": "例如：专业、科技感、轻快友好、稳重等。",
    "色彩体系": "主要使用的色彩范围，例如：以深蓝与亮蓝为主色，搭配浅灰作为背景色，局部使用橙色强调。",
    "设计风格": "例如：极简风格、拟物设计、扁平化设计、卡片式布局等。"
  }
}
```
注意事项：

不要改变任何字段名或结构，所有字段的 key 均为中文；

只优化“区域内布局样式”字段,和"组件内的布局样式"

若组件排列本身不合理，应主动调整布局策略并说明；

若 BBox 明显长条状 → 倾向横向排列，若近似方形 → 倾向网格或纵向排列；

最终输出必须为一个完整的、可被正则 pattern = r"```json\s*([\s\S]*?)\s*```" 正确解析的 JSON 文本，且包裹在三个反引号 json 和 中。
"""

intent_to_spec_prompt = """
You are a senior UI designer, skilled at generating complete UI page structure specifications based on the user's design intent, component requirements, layout descriptions, and style guidelines.

I will provide you with a piece of user input, which may include:

* Desired design goals or intent (e.g., a sales data dashboard, a user management admin panel, etc.)
* Required components (e.g., charts, tables, filter bars, etc.)
* Page layout structure (e.g., top navigation + left sidebar + main content area)
* Color scheme or design style (e.g., tech blue, card-style layout, light gray background, etc.)

Your tasks are:

1. **Understand the user's design intent, page structure, component functionality, and style requirements;**
2. **Generate a structured UI Page Specification (SPEC)** in the following format, which must be complete and adhere to the field definitions;
3. **Reasonably fill in missing information**: if component details or layout styles are not clearly specified, make logical assumptions based on common design conventions;
4. **Do not include any explanatory text**, output only the JSON structure directly, ensuring it can be used directly by frontend engineers.

User input:
{user_input}

Output format (must strictly follow the structure below):

```json
{{
  "UIDescription": {{
    "OverallDescription": "A brief overview of the page's design style and overall visual layout characteristics, e.g., clean and modern style with a well-structured layout centered around card-based modules.",
    "FunctionSummary": "A summary of the main functional features implemented on the page, such as displaying product information, supporting filter and search, displaying statistical charts, etc.",
    "ProductScenario": "Explanation of the business or usage scenario this page is designed for, such as e-commerce admin dashboard or SaaS data analytics platform.",
    "TargetUsers": "Clearly defines the user group the page is intended for, such as operations staff, data analysts, general consumers.",
    "CoreFunctions": "A focused list of essential primary functions on the page that support key business needs."
  }},
  "PageStructure": {{
    "SectionDivision": [
      {{
        "SectionID": "Should be uniquely identified, e.g., 1, 2, 3.",
        "SectionName": "Concise naming, e.g., Top Navigation Bar, Sidebar, Main Content Area.",
        "Location": "Clearly describes the section’s relative position on the page, its relation to other sections, and the proportion it occupies (e.g., top section spans 100% width of the page, occupies 10% of the page height).",
        "BBox": "Boundary box coordinates of the section, in the format: x1, y1, x2, y2 (top-left and bottom-right coordinates).",
        "LayoutStyleWithinSection": "Detailed description of how components are arranged within the section (e.g., horizontal layout, vertical layout, grid layout), alignment style, spacing ratios, etc.",
        "ContainedComponents": [
          {{
            "ComponentID": "Use the pattern: section ID + component order, e.g., 1.1, 1.2, 2.1.",
            "ComponentType": "Strictly use Ant Design component names (e.g., Button, Table, Form, Tabs, Card, etc.).",
            "Functionality": "Describe the specific function of this component from the perspective of the page’s features, e.g., 'input for filter criteria', 'data display', etc.",
            "InformationCarried": "Describe the information within the component based on an object model. For tables, list: total rows, header fields, and data fields per row. For charts, list: total data items, each item’s name and corresponding value. The information should be complete and not omitted.",
            "ComponentColorStyle": "Describe the color of different parts of the component, e.g., button with dark background and white text, light gray border.",
            "ComponentPosition": "Describe the component’s relative position within the section (e.g., aligned left, right, top, bottom, center), its relation to adjacent components, and space occupancy.",
            "ComponentLayoutStyle": "Explain how elements inside the component are arranged (e.g., text vertically centered in button, chart arranged vertically, table as vertically scrollable list), and describe size ratios, spacing, and alignment of each element."
          }}
        ]
      }}
    ]
  }},
  "VisualStyle": {{
    "OverallTone": "E.g., professional, tech-savvy, light and friendly, steady, etc.",
    "ColorScheme": "Main color range used, e.g., deep blue and bright blue as primary colors, with light gray as background, and orange for highlights.",
    "DesignStyle": "E.g., minimalistic, skeuomorphic, flat design, card-style layout, etc."
  }}
}}

```
"""

page_prompt = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整信息，并给出尽可能还原的UI描述。
我会向你提供一张UI图片，在这张图片上用红色方框标注出了UI中的各个区域。你的任务是从以下信息维度全面解析UI中的内容，并尽可能详细地还原其设计细节。
你给出的UI描述应包括以下三个部分：
1.UI描述：提供整体的页面信息，包括整体描述、核心功能
2.页面布局：利用页面中标注出的各个区域，描述页面的布局情况。在描述中，对每一个区域必须介绍该区域承担的功能，在页面中的位置，区域间的相对位置关系，但不要介绍区域内包含的具体组件。
3.视觉风格：包括整体调性、色彩体系、设计风格。其中，色彩体系对于各个颜色的描述要采用一些修饰词尽量准确描述颜色。
```json
{
  "UI描述": {
    "整体描述": "",
    "核心功能": ""
  },
  "页面布局": "",
  "视觉风格": {
    "整体调性": "",
    "色彩体系": "",
    "设计风格": ""
  }
}
```
"""


# 6.24 CWK YJX 合并版本
page_prompt_v2 = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整信息，并给出尽可能还原的UI描述。
我会向你提供一张UI图片，在这张图片上用红色方框标注出了UI中的各个区域。你的任务是从以下信息维度全面解析UI中的内容，并尽可能详细地还原其设计细节。
你给出的UI描述应包括以下三个部分：
1.UI描述：提供整体的页面信息，包括整体描述、核心功能、产品场景。
3.视觉风格：包括整体调性、色彩体系、设计风格。其中，色彩体系对于各个颜色的描述要采用一些修饰词尽量准确描述颜色。
以下是一段json格式的参考，严格按照这个结构进行输出：
```json
{
  "UI描述": {
    "整体描述": "",
    "核心功能": "",
    "产品场景": ""
  },
  "视觉风格": {
    "整体调性": "",
    "色彩体系": "",
    "设计风格": ""
  }
}
```
** 请注意遵从以下要求：
**1. 区域和组件的拆分需要合理，具有整体性和模块化。页面主体部分的区域应当按照横向楼层的概念进行划分。**
**2. json示例中提出了各个部分提取的详细要求，请严格遵守各部分对应的要求进行，不要省略或编造。
**3. 描述的信息需要能够帮助前端工程师采用React框架，使用Ant Design组件库和Recharts图表库还原出页面
"""

text_to_spec_prompt = """
你是一位经验丰富的UI设计师,擅长将用户的需求文本转换为UI设计规范。
我会向你提供一段用户需求文本，你的任务是将其转换为一个符合UI设计规范的JSON格式描述。
请根据以下要求进行转换，严格按照这个结构进行输出：
```json
{
  "UI描述": {
    "整体描述": "简要概述该页面的设计风格和整体视觉布局特点，例如：简洁现代风，布局规整，以卡片为核心模块。",
    "功能简述": "归纳页面实现的主要功能点，例如：展示产品信息、支持筛选搜索、展示统计图表等。",
    "产品场景": "说明该页面所处的业务场景或使用场景，例如：电商后台管理、SaaS数据分析平台。",
    "目标用户": "明确页面面向的用户群体，例如：运营人员、数据分析师、普通消费者。",
    "核心功能": "重点列出页面不可或缺的主要功能，聚焦于页面支撑的关键业务需求。"
  },
  "页面构成": {
    "区域划分": [
      {
        "区域编号": "应唯一标识，例如：1、2、3。",
        "区域名称": "简洁命名，例如：顶部导航栏、侧边栏、主内容区。",
        "所处的位置": "明确描述区域在整个页面的相对位置、与其他区域的关系、所占比例（例如：顶部区域横跨页面100%宽度，占页面高度10%）。",
        "区域内布局样式": "详细描述区域内各组件的排列方式（如：横向排列、纵向排列、网格排列等）、对齐方式、间距比例等。",
        "包含组件": [
          {
            "组件编号": "规则为区域编号+组件顺序，例如：1.1、1.2、2.1。",
            "组件类型": "严格使用Ant Design组件名称（例如：Button、Table、Form、Tabs、Card等）。",
            "承担的功能": "从页面功能出发，描述该组件承担的具体功能点，例如：‘筛选条件输入’、‘数据展示’等。",
            "承载的信息": "以信息对象模型描述组件内包含的信息。若为表格，请列出：总行数、表头字段、每行的字段信息。若为图表，请列出：总数据条数、每条数据的名称及对应数值等。信息应完整、不可省略。",
            "组件的配色样式": "文本描述组件中不同部分的颜色，例如：按钮为深色背景搭配白色文字，边框为浅灰色。",
            "所处的位置": "描述组件在所在区域内的相对位置（例如：居左、居右、顶部、底部、中间），以及与相邻组件的关系及占比。",
            "组件内的布局样式": "说明组件内的元素排列方式（例如：按钮文本垂直居中，图表纵向排列，表格为纵向滚动列表），并描述各元素的大小比例、间距、对齐等。"
          }
        ]
      }
    ]
  },
  "视觉风格": {
    "整体调性": "例如：专业、科技感、轻快友好、稳重等。",
    "色彩体系": "主要使用的色彩范围，例如：以深蓝与亮蓝为主色，搭配浅灰作为背景色，局部使用橙色强调。",
    "设计风格": "例如：极简风格、拟物设计、扁平化设计、卡片式布局等。"
  }
}
```

** 请注意遵从以下要求：
**1. 区域和组件的拆分需要合理，具有整体性和模块化。页面主体部分的区域应当按照横向楼层的概念进行划分。**
**2. json示例中提出了各个部分提取的详细要求，请严格遵守各部分对应的要求进行，不要省略或编造。
**3. 描述的信息需要能够帮助前端工程师采用React框架，使用Ant Design组件库和Recharts图表库还原出页面
"""

image_reference_prompt = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整信息，并给出尽可能还原的UI描述。
以下是一段json格式的参考，严格按照这个结构进行输出：
```json
{
    "承担的功能": "从页面功能出发，描述该组件承担的具体功能点，例如：‘筛选条件输入’、‘数据展示’等。",
    "承载的信息": "以信息对象模型描述组件内包含的信息。若为表格，请列出：总行数、表头字段、每行的字段信息。若为图表，请列出：总数据条数、每条数据的名称及对应数值等。信息应完整、不可省略。",
    "布局样式": "",
    "组件的配色样式": "文本描述组件中不同部分的颜色，例如：按钮为深色背景搭配白色文字，边框为浅灰色。",
    "所处的位置": "描述组件在所在区域内的相对位置（例如：居左、居右、顶部、底部、中间），以及与相邻组件的关系及占比。",
    "组件内的布局样式": "说明组件内的元素排列方式（例如：按钮文本垂直居中，图表纵向排列，表格为纵向滚动列表），并描述各元素的大小比例、间距、对齐等。"
}
```
"""

color_extract_prompt = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取页面的颜色体系。
我会提供一张UI页面截图，请你从以下维度完整提取该页面的配色方案：

1. 页面主色：页面中最常使用的颜色，通常用于主按钮、标题、图表主色等。
2. 辅助色：用于图表、标签、分区等区域的辅助颜色。
3. 背景色：页面的主背景、卡片背景等使用的颜色。
4. 字体颜色：正文、标题、次级文字等使用的颜色。
5. 高亮色：用于强调按钮、标签或告警的颜色。
6. 中性色系：用于分隔线、边框、阴影等的灰色系颜色。

**注意事项**
- 请使用简洁的中文描述颜色（如“深蓝色”、“浅灰色”、“亮橙色”等），并尽量结合视觉风格加以修饰（如“柔和的淡蓝色”、“醒目的红色”）。
- 如果某一类颜色在页面中未出现，请写“未明显出现”。
- 只返回如下格式的JSON结构，**不要包含解释说明或任何其他文字**。

```json
{
  "页面主色": "",
  "辅助色": [],
  "背景色": "",
  "字体颜色": {
    "标题": "",
    "正文": "",
    "辅助文字": ""
  },
  "高亮色": "",
  "中性色系": []
}
"""

layout_extract_prompt = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取布局信息。

我将提供一张UI页面截图，请你从布局角度进行如下结构化分析，并以 JSON 格式返回：
你将处理的图像尺寸为：宽度 1200px，高度 900px。请你根据该尺寸返回 bbox 信息，格式为 "x, y, width, height"，所有坐标值以像素为单位，基于该画布计算。
- 页面整体布局：页面采用了什么布局方式？如上下结构、左右结构、网格布局、多栏分区等。
- 区域划分方式：页面被划分为哪些功能区域？每个区域所占比例是多少？其在页面中的位置？
- 区域之间的排列关系：区域之间是如何对齐、分布的？是否有均匀间距、边框分隔？
- 对齐与间距风格：页面组件在水平和垂直方向的对齐方式（如左对齐/居中对齐）、组件之间的间距是否规整？
- 滚动行为：页面是否具有垂直/水平滚动？是整页滚动还是局部滚动？

请严格按照以下 JSON 模板输出，**不得添加解释说明或非结构化文本**：

```json
{
  "页面整体布局": "",
  "区域划分方式": [
    {
      "区域名称": "",
      "位置说明": "",
      "占比说明": "",
      "bbox": "x, y, width, height"
    }
  ],
  "区域排列关系": "",
  "对齐与间距风格": "",
  "滚动行为": ""

示例:
{
  "页面整体布局": "上下结构，顶部为导航栏，下方为主内容区与侧边栏并排",
  "区域划分方式": [
    {
      "区域名称": "顶部导航栏",
      "位置说明": "页面顶部，横向铺满",
      "占比说明": "高度占比约10%",
      "bbox": "0, 0, 1200, 100",
      
    },
    {
      "区域名称": "侧边栏",
      "位置说明": "页面左侧，竖向排列",
      "占比说明": "宽度占比约20%",
      "bbox": "0, 100, 240, 900"
    },
    {
      "区域名称": "主内容区",
      "位置说明": "页面右侧，占据主视图",
      "占比说明": "宽度占比约80%",
      "bbox": "240, 100, 960, 900",
      "包含组件": [
      {
        "组件类型": "",
        "组件所处的位置": "",
        "承担的功能": "",
        "承载的信息": ""
      }
    ]
    }
  ],
  "区域排列关系": "顶部区域在上，侧边栏与主内容区并排",
  "对齐与间距风格": "整体左对齐，区域间留有16px内边距",
  "滚动行为": "主内容区可垂直滚动"
}
"""


region_extract_prompt = """
你是一位经验丰富的UI设计专家，擅长从UI截图中精确划分功能区域。

我会提供一张UI页面截图，请你从以下角度提取页面中的**功能区域划分**信息。每个区域可以包含一个或多个组件，只要它们在功能或视觉上属于一个完整的区块。

你的输出应为一个结构化的 JSON，每个区域应包括以下字段：

1. 区域编号（从1开始编号）
2. 区域名称（基于区域功能命名，例如“筛选栏”、“图表分析区”、“数据概览”）
3. 区域所处位置（描述其在页面中的位置，如“顶部横向占满”、“居中偏左”、“底部右侧”等）
4. 区域功能说明（简要描述该区域完成的任务）
5. 包含的组件列表（每个组件应包括下列字段）：
   - 组件类型（使用 Ant Design 命名）
   - 组件所处的位置（在该区域内的相对位置，如“左侧对齐”、“顶部居中”）
   - 承担的功能
   - 承载的信息（包括字段、数据项等）

请严格按照以下结构输出，不要添加任何解释性文字：

```json
[
  {
    "区域编号": "1",
    "区域名称": "",
    "区域所处位置": "",
    "区域功能说明": "",
    "包含组件": [
      {
        "组件类型": "",
        "组件所处的位置": "",
        "承担的功能": "",
        "承载的信息": ""
      }
    ]
  }
]

"""

page_prompt_cwk = """
You are an experienced UI designer skilled at accurately extracting complete information from UI screenshots and producing detailed, faithful UI descriptions.

Based on the UI image I will provide, please conduct a comprehensive analysis of the interface by covering the following informational dimensions. Your goal is to reconstruct the UI’s design details as precisely and thoroughly as possible.

I will give you a JSON template. Please follow the structure of this template exactly when describing the UI.

The output should consist of two main parts:

UI Design Specification: Provide general UI information, including a global_color_scheme, global_style_traits, and Layout.

Page Structure: Organize the UI content in three hierarchical levels—Page → Region → Component. Each level should include its corresponding detailed attributes as defined in the template.

Below is a sample JSON format. Please strictly follow this structure in your output:
{
  "UI Design Specification": {
    "global_color_scheme": // You must extract the color in the page, must not be fabricated
    "primary": {
      "token": "color.primary",
      "value": "",
      "usage": ""
    },
    "secondary": {
      "token": "color.secondary",
      "value": "", // If not present, write "not prominently used"
      "usage": ""
    },
    "background": {
      "token": "color.background",
      "value": "",
      "usage": ""
    },
    "text": {
      "token": "color.text.primary",
      "value": "",
      "usage": ""
    },
    "accent": {
      "token": "color.accent",
      "value": "",
      "usage": ""
    }
  },
    "global_style_traits": {
    "shape": {
      "token": "shape.borderRadius.medium",
      "value": "",
      "usage": ""
    },
    "shadow": {
      "token": "elevation.level2",
      "value": "",
      "usage": ""
    },
    "spacing": {
      "token": "spacing.base",
      "value": "",
      "usage": ""
    },
    "typography": {
      "font_family": "",
      "heading_weight": "",
      "body_weight": "",
      "usage": ""
    },
    "icon_style": {
      "token": "icon.style",
      "value": "",
      "usage": ""
    },
    "border_style": {
      "token": "border.separator",
      "value": "",
      "usage": ""
    }
  }
    "Layout": {
  "layout_type": "",                      // 布局方式：grid / flex / absolute / flow
  "grid": {
    "columns": ,                            // 栅格列数
    "gutter": ,                             // 栏间距 (px)
    "margin": ,                       // 页面左右边距
    "padding":                      // 页面上下内边距
  },
  "sections": [                               // 页面区域结构（建议按照物理顺序列出）
  ],
  "spacing_scale": [4, 8, 16, 24, 32],        // 用于 padding/margin 的标准值
},
  },
  "page_structure": {
  "region_division": [
    {
      "region_name": "Name this region based on the functional role it serves within the page.",
      "region_position_on_page": "Clearly describe the region's relative location on the page, including its alignment with other regions and its proportional area within the overall layout.",
      "component_layout_within_region": "Clearly describe the spatial arrangement of components within this region, including alignment in width and height, spacing between components, and their relative proportions.",
      "contained_components": [
        {
          "component_type": "Use component names that closely match those in the Ant Design component library.",
          "functional_role": "Describe the specific function this component serves from the perspective of the entire page.",
          "information_carried": "Describe the information structure within the component in the form of an information object model. For tables, specify the total number of rows, and extract each header and body item. For charts, specify the number of data entries and extract each entry along with its corresponding value. Do not omit any required details.",
          "internal_layout_style": "Clearly describe the layout pattern used within the component, such as horizontal, vertical, or zigzag, and provide a detailed description of the spatial arrangement of all internal elements."
        }
      ]
    }
  ]
}
Please adhere to the following requirements:

1. You must strictly follow the detailed extraction requirements specified in the JSON schema. Do not omit or fabricate any content. For each field, provide the most detailed and comprehensive description possible. For the field "component_detailed_description", your response must contain no fewer than 8 complete sentences and at least 120 words.

2. You must divide the UI into different regions based on their distinct functional roles. Do not leave out any regions. The identified regions must collectively cover the entire area of the UI image without gaps.

3. You must extract all UI components from each region with complete granularity. Do not merge multiple components into a single description. If a component contains inner elements, describe them in the "component_detailed_description" or "information_carried" fields.

4. All extracted information must be detailed enough to allow a front-end engineer to accurately reconstruct the UI using React, the Ant Design component library, and Recharts for chart rendering.

"""

page_prompt_CYN = """
You are an experienced UI designer skilled at accurately extracting complete information from UI screenshots and producing detailed, faithful UI descriptions.

Based on the UI image I will provide, please conduct a comprehensive analysis of the interface by covering the following informational dimensions. Your goal is to reconstruct the UI’s design details as precisely and thoroughly as possible.

I will give you a JSON template. Please follow the structure of this template exactly when describing the UI.

The output should consist of two main parts:

UI Design Specification: Provide general UI information, including a global_color_scheme, global_style_traits, and Layout.

Page Structure: Organize the UI content in three hierarchical levels—Page → Region → Component. Each level should include its corresponding detailed attributes as defined in the template.

Below is a sample JSON format. Please strictly follow this structure in your output:
{
  "UI Design Specification": {
    "global_color_scheme": // You must extract the color in the page, must not be fabricated
    "primary": {
      "token": "color.primary",
      "value": "",
      "usage": ""
    },
    "secondary": {
      "token": "color.secondary",
      "value": "", // If not present, write "not prominently used"
      "usage": ""
    },
    "background": {
      "token": "color.background",
      "value": "",
      "usage": ""
    },
    "text": {
      "token": "color.text.primary",
      "value": "",
      "usage": ""
    },
    "accent": {
      "token": "color.accent",
      "value": "",
      "usage": ""
    }
  },
    "global_style_traits": {
    "shape": {
      "token": "shape.borderRadius.medium",
      "value": "",
      "usage": ""
    },
    "shadow": {
      "token": "elevation.level2",
      "value": "",
      "usage": ""
    },
    "spacing": {
      "token": "spacing.base",
      "value": "",
      "usage": ""
    },
    "typography": {
      "font_family": "",
      "heading_weight": "",
      "body_weight": "",
      "usage": ""
    },
    "icon_style": {
      "token": "icon.style",
      "value": "",
      "usage": ""
    },
    "border_style": {
      "token": "border.separator",
      "value": "",
      "usage": ""
    }
  }
    "Layout": {
  "layout_type": "[Specify the overall page structure type, such as sidebar+main, grid-layout, navbar+content, etc.]",
  "regions": [
    {
      "name": "[Region name, e.g., Sidebar, Topbar, Main Content]",
      "position": "[The region's position relative to the page, such as left, top, center-right]",
      "alignment": "[Content alignment within the region, such as left, center, right, stretch]",
      "size_percent": {
        "width": "[Width of the region as a percentage of the page, e.g., 20%, 80%]",
        "height": "[Height of the region as a percentage of the page, or fixed height, e.g., 100%, auto, 60px]"
      },
      "layout_inside": "[Layout method inside the region, e.g., vertical menu, horizontal, grid, flex-row]",
      "content_type": "[Functional category of the region, e.g., navigation, dashboard, card, form, media]",
      "components": [
        "[Component 1, e.g., logo]",
        "[Component 2, e.g., menu list]",
        "[Component 3, e.g., search bar]",
        "... (List all sub-components)"
      ]
    },
    "... (Repeat the above structure for any additional regions)"
  ]
},
  "page_structure": {
  "region_division": [
    {
      "region_name": "Name this region based on the functional role it serves within the page.",
      "region_position_on_page": "Clearly describe the region's relative location on the page, including its alignment with other regions and its proportional area within the overall layout.",
      "component_layout_within_region": "Clearly describe the spatial arrangement of components within this region, including alignment in width and height, spacing between components, and their relative proportions.",
      "contained_components": [
        {
          "component_type": "Use component names that closely match those in the Ant Design component library.",
          "functional_role": "Describe the specific function this component serves from the perspective of the entire page.",
          "information_carried": "Describe the information structure within the component in the form of an information object model. For tables, specify the total number of rows, and extract each header and body item. For charts, specify the number of data entries and extract each entry along with its corresponding value. Do not omit any required details.",
          "internal_layout_style": "Clearly describe the layout pattern used within the component, such as horizontal, vertical, or zigzag, and provide a detailed description of the spatial arrangement of all internal elements."
        }
      ]
    }
  ]
}
Please adhere to the following requirements:

1. You must strictly follow the detailed extraction requirements specified in the JSON schema. Do not omit or fabricate any content. For each field, provide the most detailed and comprehensive description possible. For the field "component_detailed_description", your response must contain no fewer than 8 complete sentences and at least 120 words.

2. You must divide the UI into different regions based on their distinct functional roles. Do not leave out any regions. The identified regions must collectively cover the entire area of the UI image without gaps.

3. You must extract all UI components from each region with complete granularity. Do not merge multiple components into a single description. If a component contains inner elements, describe them in the "component_detailed_description" or "information_carried" fields.

4. All extracted information must be detailed enough to allow a front-end engineer to accurately reconstruct the UI using React, the Ant Design component library, and Recharts for chart rendering.

"""

spec_prompt_1 = """
你是一位经验丰富的UI设计师，擅长从UI截图中精准提取完整的信息，并给出尽可能还原的UI描述。
请根据我所提供的UI图片，从以下的信息维度全面解析UI中的内容，并尽可能详细地还原其设计细节。我将给你一个json模板，请按照我提供的模板来对UI进行描述。
其中包括2个部分：
1.UI描述：提供整体的页面信息，包括整体描述、产品场景、核心功能
2.页面构成：按照页面-区域-组件三个层级，每个层级包括对应的详细信息。
以下是一段json格式的参考，严格按照这个结构进行输出：
{
  "UI设计规范": {
    "整体描述": "",
    "产品场景": "",
    "核心功能": "",
    "全局设计风格": "需要详细描述UI整体的外观，从布局、颜色、风格三个方面(不少于8句话，不少于120字)",
  },
  "页面构成": {
    "区域划分": [
      { 
        "区域名称": "按照区域所承担的功能为这个区域命名",
        "区域所在页面位置":"应当清晰描述区域所在页面的相对位置，以及与其他区域的对齐关系，区域在占整个页面的比例",
        "区域内各组件布局":"应当清晰描述区域内各组件的排版布局，各个组件之间高度宽度的对齐关系，间距，比例大小等信息",
        "包含组件": [
          { 
            "组件类型": "需要尽量贴近ant design组件库的组件名称",
            "承担的功能": "从页面整体出发，描述该组件的具体功能。",
            "承载的信息": "组件中的信息应以信息对象模型的形式完整再现。对于表格，应写出表格共计多少行，并提取表头和表体中的每一项。对于图表，应该给出有几个数据条目，并提取每个条目，以及条目对应的数据。不要省略要求中的任何信息",
            "组件内的布局样式":"应当清晰写出组件内的排版布局，横向、纵向或者z字形等排版样式，并清晰描述组件内各元素的布局。"
          }
        ]
      }
    ]
  }
}
** 请注意遵从以下要求：
**1. json示例中提出了各个部分提取的详细要求，请严格遵守各部分对应的要求进行，不要省略或编造。对于每个字段，你需要提供尽可能细节、详尽的描述。对于"组件详细说明"字段，不少于8句话，不少于120字
**2. 你需要根据不同的功能将UI划分为不同的区域。你不能遗漏任何区域。识别出的区域必须覆盖完整的UI图片。
**3. 你必须从划分的区域中完整地识别到所有粒度的UI组件，不能遗漏任何UI组件，不要把多个组件合并到一个组件中进行说明。包含在组件内部的元件则填写在组件详细说明或者承载的信息字段中。
**4. 描述的信息需要能够帮助前端工程师采用React框架，使用Ant Design组件库和Recharts图表库还原出页面
**5. 输出json的key严格按照模板进行输出，不能翻译成英文
"""

overall_design_spec_prompt_cn = """
# UI 分析说明手册

## 角色定义

你是一名经验丰富的 UI 设计师，擅长从 UI 截图中准确提取完整信息，并提供高度详细且忠实的 UI 描述，使用中文。

## 任务

请根据我提供的截图，按照下方列出的信息维度分析 UI 内容，并尽可能精确地重构设计细节。
你必须严格遵循所给的 JSON 模板。


## 结构概览

模板分为 **两大部分**：

### 1. 全局 UI 设计规范

提供页面整体的设计原则与样式，包括：

* **Layout Structure**（布局结构）
* **Color System**（色彩系统）
* **Shape Language**（形态语言）
* **Usage Scenario**（使用场景）


### 2. 页面组成

将 UI 按层级结构拆解为三层：

```
Page → Section → Component
```

每一层都包含描述位置、功能、布局和内容的详细字段。

## 约束条件

### 1. 严格的字段要求

* JSON 示例中的所有字段都必须填写。字段的类型必须都是String。 Color_Scheme的值必须是String。
* **不得省略或虚构**任何部分。
* **"UI Design Specification"** 必须包含 **至少 8 个完整句子** 且 **不少于 120 个中文字数**。
* 描述必须是**参数化**的，不得含糊或带有情感色彩。

### 2. 区块识别

* 按**功能**将 UI 拆分为多个 Section。
* **不可遗漏**任何 Section——页面上的每个可见区域都必须覆盖。
* Section 之间必须**共同覆盖整个 UI 图像**。

### 3. 组件提取

* 在每个 Section 中识别出**所有 UI 组件**。
* **不可将多个组件合并为一个**。
* 内部元素（如图标、标签）必须在 **Component Layout Style** 中描述。

### 4. 面向开发者的输出

你的描述必须是**开发可直接使用**的：

* 必须支持 **React 框架** 重现
* 必须使用 **Ant Design** 组件
* 图表必须使用 **Recharts**

## JSON 模板（参考格式）

```json
  {
    "UI_Design_Specification": {
    "Layout_Structure": "页面采用固定宽度的桌面画布并居中于视口，外边距较大。布局基于 12 列网格：固定左侧边栏约占 20% 宽度，右侧主画布占剩余约 80%，并采用两行多列卡片网格结构。基础间距单位为 8px；内部列间距为 16px，主要区块间距为 24–32px。垂直节奏遵循 标题 → 内容 → 元信息 的模式，卡片内部垂直堆叠间距为 8/12/16px。内容在列内左对齐，标题区工具栏使用两端对齐。卡片保持一致的内边距（约 24px）和相同的圆角半径；图表与列表均对齐到相同的网格线。顶部工具区（搜索、操作按钮、用户信息）位于主画布第一行。内容密度为中等，优化为快速浏览和轻量交互。所有模块均为独立卡片，以便在响应式 React/Ant Design 网格中支持重排。",
    "Color_System": "#FFFFFF 34.41%, #F7F3FB 15.95%, #F2EDF9 14.12%, #E1DFF9 12.63%, #CF9BDE 6.47%, #F4F4FB 4.86%, #FBF9FD 4.23%, #F3E8FB 4.00%, #E5EAF9 3.03%, #F5EFEF 0.29%。少量强调色低于 0.5%，包括 #7EE5BE (~0.14%) 和 #F6AB76 (~0.20%)。建议的抽象色彩角色（不改变比例）：分层背景使用接近白色的淡紫色调；强调色取自饱和的紫色 (#CF9BDE) 及少量青色/橙色点缀。在中灰色文字放置于浅色背景时，应保持文字对比度满足 WCAG AA 标准（正文目标对比度 4.5:1）。",
    "Shape_Language": "整体几何形态柔和圆润。圆角半径分为约 12/16/24px 三档，适用于卡片、胶囊形按钮和输入框；头像为圆形。描边细致（1px 中性色边框），分隔线透明度高且低调。阴影分为三级：低（y2 blur8）、中（y6 blur16）、高（y12 blur24），透明度较低以保留浅色系美感。按钮和标签为胶囊形。图标圆润简洁，避免尖锐边角。图表使用平滑曲线和圆角数据点。插画风格为扁平化，轮廓较粗且圆润，配色与紫色强调色系一致。",
    "Usage_Scenario": "该设计适用于监控与快速访问型的仪表盘。用户通过浏览摘要、查看时间序列图表、核对列表、触发小型操作（如筛选或打开详情）来完成任务。交互节奏以快速浏览为主，偶有点击操作，非重度表单输入。信息以卡片方式分块呈现，使用户可以快速获取关键指标、跟踪进度、阅读简要备注。导航区固定在左侧，右侧主画布根据需要切换内容模块。布局支持频繁的上下文切换和轻量决策。视觉上突出趋势与简短状态信息。设计旨在鼓励用户快速深入查看，而非长时间数据录入。"
  },
  "Page_Composition": {
    "Sections": [
      {
        "Section_Name": "以抽象功能原型命名该区块（如 'Global Navigation', 'Hero Banner', 'Entity_List', 'KPI Panel'），避免使用产品特定名称。",
        "Data_Section_Id": "Adding a unique id as an attribute to a React component allows you to directly access this element using querySelector",
        "Section_Position_on_Page": "使用网格比例和相邻关系描述相对位置（如 '固定左侧边栏占 ~20% 宽度；右侧为主内容区'、'页面最顶部的全宽横幅'）。需提及堆叠顺序及大致比例。",
        "Component_Layout_in_Section": "说明内部布局模式（垂直堆叠、水平排列、N×M 网格）、间距刻度（8px 的倍数）、对齐方式（起始/居中/末端）、以及大小比例（图标:文字:操作 ≈ 1:3:1）。避免出现内容语义。",
        "Color_Scheme": "列出该区块的主色及其 HEX 值与角色（如 '主背景——#FFFFFF', '强调色——#FF4D4F'），不得包含功能性描述。",
        "Contained_Components": [
          {
            "Component_Type": "从 Ant Design 组件类型中选择（Menu, Card, List, Statistic, Avatar, Button, Input.Search, Tabs, Table, Tag, Empty, Pagination）。",
            "Data_Component_Id": "Adding a unique id as an attribute to a React component allows you to directly access this element using querySelector",
            "Function": "描述通用的用户体验功能（导航、搜索、筛选、显示摘要、触发深入操作），不得使用领域特定用语。",
            "Component_Layout_Style": "说明内部排列（图标 + 标签行、标题-副标题堆叠、左媒体右元信息、双列标签-值），并用抽象单位（8px 倍数）指定对齐与间距。",
            "Color_Scheme": "列出该组件的主色及其 HEX 值与角色（如 '主背景——#FFFFFF', '强调色——#FF4D4F'），不得包含功能性描述。",
          }
        ]
      }
    ]
  }
}
```
"""
overall_design_spec_prompt = """

# UI Analysis Instruction Manual

## Role Definition

You are an experienced UI designer with expertise in accurately extracting comprehensive information from UI screenshots and providing highly detailed and faithful UI descriptions.

## Task

Please analyze the UI content based on the screenshot I provide, using the information dimensions listed below, and reconstruct the design details as precisely as possible.

You must follow the JSON template provided strictly.

---

## Structure Overview

The template consists of **two main parts**:

### 1. Global UI Design Specification

Provides the overall design principles and styling of the page, including:

- **Layout Structure**
- **Color System**
- **Shape Language**
- **Usage Scenario**

---

### 2. Page Composition

A hierarchical breakdown of the UI into three levels:

```

Page → Section → Component

```

Each level includes detailed fields to describe position, function, layout, and content.

---

## Constraints

### 1. Strict Field Requirements

- All fields in the JSON example must be filled in.
- Do **not omit or fabricate** any part.
- **"UI Design Specification"** must contain **at least 8 complete sentences** and be **no less than 120 words**.
- Descriptions must be **parameterized**, not vague or emotional.

---

### 2. Section Identification

- Divide the UI into **multiple sections based on functionality**.
- Do **not miss any section**—every visible region must be covered.
- Sections must **collectively cover the entire UI image**.

---

### 3. Component Extraction

- Identify **all UI components** within each section.
- Do **not merge multiple components** into one.
- Inner elements (like icons, labels) must be described under **Component Layout Style**.

---

### 4. Developer-Oriented Output

Your descriptions should be **developer-ready**:

- Must support reproduction using the **React framework**
- Must use **Ant Design** components
- For charts, use **Recharts**

---

## JSON Template (Reference Format)

```json
{
  "UI_Design_Specification": {
    "Layout_Structure": "The page uses a fixed-width desktop canvas centered in the viewport with generous outer padding. A 12-column grid underlies the layout: a fixed left rail occupies ~20% width and the main canvas spans the remaining ~80% as a two-row, multi-column card grid. The base spacing unit is 8px; inner gutters are 16px, and major band separations are 24–32px. Vertical rhythm follows a title → content → meta pattern with 8/12/16px stacks inside cards. Items align left within columns and use space-between for header utilities. Cards share consistent padding (~24px) and equal border radii; charts and lists align to the same grid lines. Top utilities (search, actions, profile) sit on the first row of the main canvas. Content density is medium, optimized for quick scanning and light interactions. All modules are independent cards to support reflow in a responsive React/Ant Design grid.",
    "Color_System": "#FFFFFF 34.41%, #F7F3FB 15.95%, #F2EDF9 14.12%, #E1DFF9 12.63%, #CF9BDE 6.47%, #F4F4FB 4.86%, #FBF9FD 4.23%, #F3E8FB 4.00%, #E5EAF9 3.03%, #F5EFEF 0.29%. Minor accents observed but below 0.5% each include #7EE5BE (~0.14%) and #F6AB76 (~0.20%). Suggested abstract roles (without altering percentages): layered backgrounds use the near-white lilac tints; accents draw from the saturated purple (#CF9BDE) and small teal/orange touches. Maintain text contrast (target WCAG AA 4.5:1 for body text) when placing medium-gray text on tinted backgrounds.",
    "Shape_Language": "Overall geometry is soft and rounded. Corner radius scale appears at ~12/16/24px for cards, pills, and inputs; avatars are circular. Strokes are light (1px neutral-tinted borders) and dividers are subtle with high transparency. Shadows use three tiers: low (y2 blur8), medium (y6 blur16), and high (y12 blur24) with low opacity to preserve the pastel aesthetic. Buttons and badges are pill-like. Icons are rounded and simple, avoiding sharp corners. Charts use smooth curves and rounded data points. Illustration styles are flat with thick rounded outlines matching the purple accent family.",
    "Usage_Scenario": "This is a dashboard for monitoring and quick access. Users scan summaries, review time-series charts, check lists, and trigger small actions like filtering or opening details. The interaction tempo is scan-heavy with occasional taps and clicks, not form-heavy input. Information is chunked into cards so users can glance at KPIs, track progress, and read notes. Navigation is persistent on the left, while the right canvas rotates content tiles. The layout supports frequent context switching and lightweight decision making. Visual emphasis is given to trends and short status notes. The design encourages quick drill-ins rather than deep data entry."
    },
  "Page_Composition": {
    "Sections": [
      {
        "Section_Name": "Name the section by abstract function archetype (e.g., 'Global Navigation', 'Hero Banner', 'Entity_List', 'KPI Panel'). Avoid product-specific names.",
        "Data_Section_Id": "Adding a unique id as an attribute to a React component allows you to directly access this element using querySelector",
        "Section_Position_on_Page": "Describe relative position using grid fractions and adjacency (e.g., 'fixed left rail occupying ~20% width; main canvas to the right', 'top-most full-width band'). Mention stacking order and approximate proportions only.",
        "Component_Layout_in_Section": "Explain internal layout model (vertical stack, horizontal row, grid N×M), spacing scale (multiples of 8px), alignment (start/center/end), and size ratios (icon:text:action ≈ 1:3:1). Avoid content semantics.",
        "Color_Scheme": "List primary colors used in this section, with their HEX values and roles (e.g., 'primary surface: #FFFFFF', 'accent: #FF4D4F'). No functional descriptions.",
        "Contained_Components": [
          {
            "Component_Type": "Choose from Ant Design taxonomy (Menu, Card, List, Statistic, Avatar, Button, Input.Search, Tabs, Table, Tag, Empty, Pagination).",
            "Data_Component_Id": "Adding a unique id as an attribute to a React component allows you to directly access this element using querySelector",
            "Function": "Describe the generic UX role (navigate, search, filter, display summary, drill-in trigger). No domain-specific wording.",
            "Component_Layout_Style": "State internal arrangement (icon + label row, title-subtitle stack, media-left meta-right, two-column label-value). Specify alignment and spacing in abstract units (8px multiples).",
            "Color_Scheme": "List primary colors used in this component, with their HEX values and roles (e.g., 'label text: #595959', 'tag background: #E6F7FF'). No functional descriptions.",
          }
          }
        ]
      }
    ]
}
}

```

"""