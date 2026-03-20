<div align="center">

![AnyClaw Logo](docs/logo图/logo图.png)

# AnyClaw Agent框架

**基于 LangChain 的 Agent 框架，接入skills/tools快速搭建属于垂类Agent**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-1.0+-green.svg)](https://www.langchain.com/)
[![Rich](https://img.shields.io/badge/Rich-13.7.0+-orange.svg)](https://github.com/Textualize/rich)
[![Typer](https://img.shields.io/badge/Typer-0.9.0+-blue.svg)](https://typer.tiangolo.com/)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/yourusername/anyclaw)

</div>

---

## 📖 项目介绍

**AnyClaw** 是一个功能强大的 Agent 框架，基于 LangChain 构建，采用 ReAct（Reasoning + Acting）模式，让你能够快速开发并接入skills/tools，搭建属于自己的垂类Agent。

### 1. 核心特性

- **流式响应**：支持 token 级别的实时流式输出，提供流畅的交互体验
- **ReAct Agent**：基于 ReAct 模式的智能推理与执行框架
- **多模型支持**：支持 OpenAI、Gemini、Qwen、DeepSeek、Kimi 等多种 LLM 提供商
- **工具系统**：灵活的工具扩展机制，轻松添加自定义工具
- **Skills 元技能**：支持通过 `skills/*/SKILL.md` 注册元技能，提供标准化脚本入口（`/skills` 查看列表）
- **会话管理**：完整的会话持久化与恢复功能，支持多会话切换
- **Token 追踪**：实时追踪每次调用的 token 消耗，支持按步骤统计
- **消息压缩**：自动压缩历史消息，节省 token 成本
- **任务隔离**：每个会话拥有独立的 sandbox 目录，文件互不干扰
- **美观 CLI**：基于 Rich 的美化命令行界面，支持 Markdown 渲染
- **命令系统**：丰富的命令支持（`/new`, `/memory`, `/models`, `/tools`, `/clear`, `/exit`）

### 2. 核心定位

核心设计理念是：**只需 vibe coding专属的工具，即可改造搭建为自己的通用/垂类Agent**。

- 修改图标与欢迎语 → 个性化你的 Agent
- 修改 system prompt → 定制 Agent 的行为
- 增加tools工具/skills工具 → 扩展 Agent 能力

所有配置都通过简单的 YAML 文件和代码修改即可完成，无需深入框架底层。

---

## 🎬 功能演示

### 1. 主页界面
*-- 美观的主界面，展示项目 Logo 和所有可用命令，支持快速开始新会话或恢复历史会话*
![主页](docs/效果图/主页图.png)

### 2. 新建会话
*-- 使用 `/new` 命令创建新会话，每个会话拥有独立的 task_id 和沙箱目录，实现任务隔离*
![新建会话](docs/效果图/新建会话.png)

### 3. 工具调用
*-- Agent 智能调用工具执行任务，实时显示工具调用过程和结果，支持流式输出和 Token 追踪*
![工具调用](docs/效果图/工具调用.png)

### 4. 会话恢复
*-- 使用 `/memory` 命令查看并恢复历史会话，支持多会话管理和无缝切换，保留完整的对话历史*
![恢复记忆](docs/效果图/恢复记忆.png)

### 5. 工具列表
*-- 使用 `/tools` 命令查看所有已注册的工具，了解每个工具的功能描述和使用方式*
![工具列表](docs/效果图/工具列表.png)

### 6. 模型列表
*-- 使用 `/models` 命令查看所有配置的模型信息，包括不同场景下的模型配置（main、text_generation 等）*
![模型列表](docs/效果图/模型列表.png)

### 7. 清除记忆
*-- 使用 `/clear` 命令清除所有会话记忆和沙箱文件，需要确认操作，确保数据安全*
![清楚记忆](docs/效果图/清楚记忆.png)

---

## 🚀 快速部署

### 1. 环境要求

- Python 3.10+
- pip 或 conda

### 2. 安装步骤

（1） **克隆项目**
```bash
git clone https://github.com/wz289494/anyclaw.git
cd anyclaw
```

（2） **创建虚拟环境（推荐）**
```bash
# 创建虚拟环境
# Windows
python -m venv venv

# Linux/Mac
python3 -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

（3） **安装依赖**
```bash
pip install -r requirements.txt
```

（4） **配置环境变量**

创建 `.env` 文件，配置你的 API Key：

```env
# OpenAI
OPENAI_APIKEY=your_openai_api_key

# DeepSeek
DEEPSEEK_APIKEY=your_deepseek_api_key

# Qwen / DashScope
QWEN_APIKEY=your_qwen_api_key

# Gemini
GEMINI_APIKEY=your_gemini_api_key

# Kimi
KIMI_APIKEY=your_kimi_api_key
```

（5） **配置模型**

编辑 `config/model.yaml`，设置你使用的模型。配置文件支持多个场景，每个场景可以配置不同的模型：

```yaml
# 主流程模型：作为 ReAct Agent 的底座
main:
  provider: deepseek  # 或 openai, gemini, qwen, kimi
  model: deepseek-chat
  api_key_env: DEEPSEEK_APIKEY

# 文本生成模型：用于文本生成任务
text_generation:
  provider: qwen
  model: qwen-plus
  api_key_env: QWEN_APIKEY

# 元素提取模型：用于从文本中提取结构化信息
element_extraction:
  provider: qwen
  model: qwen-plus
  api_key_env: QWEN_APIKEY

# 代码生成模型：用于代码生成任务
code_generation:
  provider: deepseek
  model: deepseek-chat
  api_key_env: DEEPSEEK_APIKEY
```

**配置场景说明：**

- **main**：主流程模型，作为 ReAct Agent 的核心底座，负责推理和工具调用决策
- **text_generation**：文本生成模型，专门用于文本生成任务，如文章写作、内容创作等
- **element_extraction**：元素提取模型，用于从文本中提取结构化信息，如实体识别、信息抽取等
- **code_generation**：代码生成模型，专门用于代码生成任务，如代码补全、代码生成等

**支持的模型提供商：**

- **OpenAI**：OpenAI 官方 API，支持 GPT-4、GPT-3.5 等模型，稳定可靠，适合生产环境
- **Gemini**：Google 的 Gemini 系列模型，支持 gemini-pro、gemini-flash 等，性能强劲，多模态能力强
- **Qwen**：阿里云通义千问模型，支持 qwen-max、qwen-plus、qwen-turbo、qwen-coder 等，国内访问速度快，中文理解能力强
- **Kimi**：Moonshot AI 的 Kimi 模型，支持长上下文（200K tokens），适合处理长文本任务和复杂文档分析

（6） **安装项目**

安装项目到虚拟环境中（以开发模式安装，便于修改代码）：

```bash
pip install -e .
```

（7） **运行项目**
```bash
# 方式1：使用命令行入口（需要先执行 pip install -e .）
anyclaw-cli

# 方式2：直接运行（无需安装）
python -m cli.main
```

### API 模式（HTTP 服务）

```bash
anyclaw-api
```

默认监听 `0.0.0.0:7000`，提供以下接口（返回 Markdown 或 JSON）：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/tools | 工具列表（markdown） |
| GET | /api/models | 模型列表（markdown） |
| GET | /api/skills | skills 列表（markdown） |
| POST | /api/new | 创建新任务，返回 task_id |
| GET | /api/memory | 返回 task_id 列表 |
| POST | /api/clear | 清理 memory 与 sandbox |
| POST | /api/agent | 运行 agent（流式返回工具调用与最终结果） |

`/api/agent` 请求示例：

```bash
curl -N -X POST http://localhost:7000/api/agent \
  -H "Content-Type: application/json" \
  -d '{"task_id":"<task_id>","query":"你好"}'
```

服务会返回 NDJSON（逐行 JSON），包含 `tool_call`、`tool_result` 与 `final` 事件。

---

## 💡 使用技巧

### 1. 基本命令

- `/new` - 开启新的会话
- `/memory` - 查看并恢复之前的会话（最多显示5个）
- `/models` - 查看所有模型配置
- `/tools` - 查看所有可用工具
- `/skills` - 查看所有可用 skills（扫描 `skills/*/SKILL.md`）
- `/clear` - 清除 memory 和 sandbox（需确认）
- `/exit` - 退出程序

### 2. 会话管理

- 每个会话都有唯一的 `task_id`，用于隔离数据和文件
- 会话数据保存在 `memory/STM/` 目录
- 任务文件保存在 `sandbox/{task_id}/` 目录
- 使用 `/memory` 命令可以快速恢复之前的会话

### 3. Token 追踪

- 系统会自动追踪每次调用的 token 消耗
- 支持按步骤统计（agent_processing, tool_xxx 等）
- Token 使用情况会实时显示在界面上
- 历史记录保存在会话数据中

### 4. 消息压缩

- 当上下文 token 数超过限制（默认 20000）时，会自动压缩历史消息
- 压缩后的消息会生成摘要，保留关键信息
- 压缩信息会在界面上提示

---

## 🔧 Vibe coding 继续开发

想要定制自己的 Agent？很简单，跟着下面的步骤来就行。

### 1. 先让 AI 熟悉项目

开始之前，先告诉你的 coding 工具（比如 Cursor、GitHub Copilot 等）：
```
-先熟悉当前项目，了解项目结构和核心模块
```

### 2. 更换 Logo 和欢迎语

**换 Logo**：
```
-将 logo 图片放到 docs/logo图/logo图.png，替换掉原来的就行
```

**改欢迎语**：
```
-我现在需要更换项目名称为：
-修改 cli/display.py 中的 print_welcome() 函数，更换欢迎语
-修改 cli/display.py 中的 print_icon() 函数，更换 CLI 图标和 ASCII 艺术字
-修改项目中其他所有涉及 anyclaw 或 AnyClaw 的位置，更改为项目名称
```

**需要更换的文件和位置**：

1. **`pyproject.toml`**：
   - `name = "anyclaw"` → `name = "YOUR_PROJECT_NAME"`
   - `description = "anyclaw：agent框架"` → `description = "YOUR_PROJECT_NAME：agent框架"`
   - `anyclaw = "cli.main:main"` → `YOUR_COMMAND_NAME = "cli.main:main"`

2. **`cli/display.py`**：
   - `print_icon()` 函数中的 ASCII 艺术字和注释（替换 "ANYCLAW" 为 "YOUR_PROJECT_NAME"）
   - `print_welcome()` 函数中的欢迎语：`"欢迎使用 AnyClaw - Agent智能助手"` → `"欢迎使用 YOUR_PROJECT_NAME - Agent智能助手"`

3. **`cli/main.py`**：
   - 所有 `"AnyClaw"` 的显示文本 → `"YOUR_PROJECT_NAME"`

4. **`cli/interactive.py`**：
   - 所有 `"AnyClaw"` 的显示文本 → `"YOUR_PROJECT_NAME"`

5. **`utils/path.py`**：
   - 注释中的 `"anyclaw 项目所在目录"` → `"YOUR_PROJECT_NAME 项目所在目录"`

6. **`README.md`**：
   - 项目标题、描述、所有提到 AnyClaw 的地方 → `YOUR_PROJECT_NAME`
   - GitHub 链接中的用户名和仓库名 → `YOUR_GITHUB_USERNAME/YOUR_REPO_NAME`

### 3. 定制 System prompt

想让你的 Agent 更专业？更幽默？更严谨？直接改 system prompt 就行
```
-为我修改prompt system：
-设定角色：（如舆情分析助手）
-设定认知：具备React理解 + 专属理解（如舆情分析的方法）
-设定名称或性格：（如平和、热情）
```
### 4. 给 Agent 添加新能力（工具）

想让 Agent 能做更多事情？给它加工具就行

**第一步：创建工具文件**

首先，需要在 `tools/` 目录下创建一个新的 Python 文件

```
-在 tools/ 目录下新建一个文件，命名为 （my_tool.py）
工具用途说明：
工具时机说明：
工具逻辑：
工具输入参数：
工具输出参数：
-工具函数需要用 @tool 装饰器，返回值必须是 JSON 字符串格式
-输出参数字段需要包含至少其一（如 result、data、output 等）
-如果需要保存文件，必须使用任务ID作为路径，参考demo工具的文件保存处理
-工具内部需要调用 LLM 来分析数据或生成内容，可以根据场景选择合适的模型使用：如使用项目中的（text_generation、element_extraction、code_generation）
```

**第二步：导出工具**

创建好工具文件后，需要在 `tools/__init__.py` 中导出它

```
打开 tools/__init__.py，把新的工具导入并加到 __all__ 列表里
```

代码示例：

```python
from tools.my_tool import my_tool

__all__ = ["my_tool"]
```

**第三步：注册到 Agent**

最后一步，把工具注册到 Agent 的工具列表中。这样 Agent 才能知道有这个工具可以使用。

```
打开 agent/reactagent.py，找到 AGENT_TOOLS 这一行，把新的工具导入并加到列表里
```

代码示例：

```python
from tools import my_tool

# 当前注册的工具列表
AGENT_TOOLS = [my_tool]
```

**第四步：测试工具**

工具添加完成后，写一个测试文件，直接运行查看效果

```
在scripts中新增一个工具测试文件，用于测试新的工具（如my_tool）
格式按照run_demo示例一致
```

---

## 📁 项目架构

### 1. 技术栈

- **LangChain 1.0** - Agent 框架、工具系统、流式输出
- **Rich** - CLI 美化与 Markdown 渲染
- **Typer** - CLI 框架
- **PyYAML** - 配置管理
- **Python 3.10+** - 核心语言

### 2. 目录树

```
anyclaw/
├── agent/              # Agent 核心逻辑
│   ├── __init__.py
│   └── reactagent.py  # ReAct Agent 实现
├── cli/                # 命令行界面
│   ├── __init__.py
│   ├── main.py        # 主入口
│   ├── interactive.py # 交互式运行
│   ├── display.py     # 显示工具（Rich UI）
│   ├── session_ui.py  # 会话管理 UI
│   ├── tools_ui.py    # 工具列表 UI
│   ├── models_ui.py   # 模型列表 UI
│   └── clear_utils.py # 清除工具
├── config/             # 配置文件
│   ├── __init__.py
│   ├── model.yaml     # 模型配置
│   └── prompt.yaml    # Prompt 配置
├── docs/               # 文档和图片
│   ├── logo图/        # Logo 图片
│   └── 效果图/        # 功能演示图
├── memory/             # 会话存储
│   └── STM/           # 短期记忆（会话数据）
├── model/              # 模型工厂
│   ├── __init__.py
│   └── factory.py     # 模型实例化
├── prompt/             # Prompt 模板
│   └── system_prompt.txt
├── sandbox/            # 任务运行目录
├── tools/              # 工具定义
│   ├── __init__.py
│   └── xxx.py  # 示例工具
├── utils/              # 工具函数
│   ├── __init__.py
│   ├── session_manager.py  # 会话管理
│   ├── token_tracker.py    # Token 追踪
│   ├── env_loader.py        # 环境变量加载
│   ├── message_utils.py     # 消息工具（压缩、转换等）
│   ├── path.py              # 路径工具
│   ├── prompt_loader.py     # Prompt 加载
│   └── task_context.py      # 任务上下文管理
├── scripts/            # 脚本文件
│   └── run_xxx.py  # 工具测试脚本
├── pyproject.toml      # 项目配置
├── requirements.txt    # 依赖列表
├── LICENSE.txt         # 许可证
└── README.md           # 项目说明
```

---

## 📝 许可证

本项目采用 **NON-COMMERCIAL LEARNING LICENSE 1.1**（非商业学习许可证）。

### 许可证说明

Copyright (c) 2024 relakkes@gmail.com

本软件及其相关文档文件（以下简称"软件"）在以下条件下授权使用：

#### 授权范围

版权所有者授予任何接受本许可证的自然人或法人实体（以下简称"用户"）免费、非独占、不可转让的权利，以非商业学习为目的使用、复制、修改和合并本软件。

#### 使用条件

1. 用户必须在软件及其副本的所有合理显著位置包含上述版权声明和本许可证声明
2. 软件仅限于学习和研究目的，不得用于大规模爬取或干扰平台运营的活动
3. 未经版权所有者书面同意，软件不得用于任何商业目的或对第三方造成不当影响

#### 免责声明

1. 软件按"现状"提供，不提供任何明示或暗示的保证，包括但不限于适销性、特定用途适用性和非侵权性的保证
2. 在任何情况下，版权所有者均不对因使用或无法使用本软件而产生的任何直接、间接、偶然、特殊、示范性或后果性损害承担责任

#### 完整许可证

完整的许可证文本请查看 [LICENSE.txt](LICENSE.txt) 文件。

**注意**：如需商业使用，请联系版权所有者获取商业许可。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐

---

<div align="center">

**Made with ❤️ by AnyClaw Team**

</div>
