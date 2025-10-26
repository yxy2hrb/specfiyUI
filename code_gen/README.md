# code_generation_derivation
# npm环境搭建
+ 安装node.js
+ npx create-react-app 项目名
+ cd 到路径
+ npm install antd recharts @ant-design/icons
+ npm start，浏览器自动打开页面
+ 之后修改react app 里面的src/app.js即可
需要重新搭建，文件夹里有一个npm文件夹，但是不好用

# 去gpt_api.py里修改需要使用的模型

# 外面测试环境
在prompt.py文件里面有code_prompt_v2，把前面生成的spec放入{spec_input}，给gpt/qwen。把返回的代码拷贝替换掉app.js的代码，npm自动重新渲染；

# 按照spec进行渲染
+ 入口是gen_code_with_allspec，作用是针对一个文件夹里面的所有json文件，尝试挨个读，json里面如果有spec_res字段，就用这个字段进行渲染，会将代码写入到CODE_PATH，并尝试读取PORT端口渲染
+ gen_code_with_allspec是批处理，需要开多个npm环境

# 我们的代码测试环境
+ 入口为gen_code_with_check，该代码作用是从一个文件夹获取图片，每个图片自动化获取spec，根据spec生成代码，生成的代码拷贝到app.js，然后调用自动化渲染工具去检测app.js能否正确渲染。如果不能渲染，会将报错信息打包返回给大模型让他debug，生成新代码。之后会对spec衍生，根据新spec再次进行上述循环
+ BASE_FOLDER是项目根目录，SRC_FOLDER是输入，DEST_FOLDER是存储生成结果的地方， CODE_PATH是npm环境的app.js代码路径，WAIT_SELECTOR不改动，PORT 是npm前端的端口，默认是3000，根据npm start时的端口修改即可
+ 接入衍生的方法，如果是修改prompt，去prompt.py里面新建一个prompt即可，然后在gen_code_with_spec.py里修改使用的prompt；如果是有自动化的生成流程，需要去改gen_code_with_spec.py里面generate_code_single和derival_spec_single函数

