<div align="center">

![AnyClaw Logo](docs/logo图/logo图.png)

# AnyClaw

**轻量化 ReAct Agent 框架，面向垂类 Agent 的快速搭建与接入**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://www.langchain.com/)
[![Rich](https://img.shields.io/badge/Rich-13.7+-orange.svg)](https://github.com/Textualize/rich)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/wz289494/anyclaw)

</div>

---

## 项目定位

**AnyClaw** 是一个面向实际落地的轻量化 ReAct Agent 框架。

它的核心目标不是做一个笨重的通用平台，而是提供一套足够轻、足够清晰、足够容易改造的 Agent 底座，让你可以通过少量 `tool` 与 `skill` 配置，快速把它改造成自己的通用 Agent 或垂类 Agent。

适合的场景包括：

- 为 App、网站或内部系统快速接入一个垂类 Agent
- 基于现有工具链快速搭建业务 Agent
- 用 `skills` 形式快速扩展文档、表格、搜索等能力
- 用 `CLI / API / Copilot` 三种形态覆盖开发、接入和演示场景

---

## 核心价值

- **轻量化框架**：项目结构直白，依赖克制，便于理解、修改和二次开发
- **ReAct Agent 底座**：基于 LangChain 的推理与工具调用流程，适合复杂任务编排
- **垂类改造友好**：通过 prompt、tool、skill、模型配置即可快速改造成领域 Agent
- **多形态交互**：同时支持 `CLI`、`HTTP API`、`浏览器 Copilot` 三种使用方式
- **可接入业务系统**：提供会话管理、任务隔离、流式输出、工具执行链路，方便外部集成

---

## 三种模式

### 1. CLI 模式

使用命令：

```bash
anyclaw-cli
```

特点：

- 适合本地开发、调试和日常使用
- 支持流式输出、工具调用、历史会话恢复
- 支持 `/new`、`/memory`、`/tools`、`/models`、`/skills`、`/clear` 等命令

### 2. API 模式

使用命令：

```bash
anyclaw-api
```

特点：

- 启动轻量 HTTP 服务，默认监听 `0.0.0.0:7000`
- 适合接入网站、App、自动化工作流或后端服务
- `/api/agent` 支持 NDJSON 流式返回，能持续输出 `tool_call`、`tool_result`、`final`

说明：

- 当前 API 形态基于 Python 内置 `http.server`，不是 FastAPI
- 设计目标是轻量、直接、易部署，适合快速接入和本地服务化

### 3. Copilot 模式

使用命令：

```bash
anyclaw-copilot
```

特点：

- 启动一个浏览器侧边栏式对话工作台，默认地址为 `http://127.0.0.1:7001`
- 默认连接本地 API：`http://127.0.0.1:7000`
- 如果本地 API 未启动，会尝试自动拉起 API 服务
- 支持会话恢复、流式对话、Agent 配置查看

可选参数：

```bash
anyclaw-copilot --no-open
anyclaw-copilot --no-api-autostart
anyclaw-copilot --api-base http://127.0.0.1:7000
```

---

## 核心功能

### 1. 短期记忆管理

- 每个会话都有独立 `task_id`
- 会话数据保存在 `memory/STM/`
- 支持基于 `task_id` 恢复对话上下文
- API 与 Copilot 都可以继续同一段记忆

### 2. 任务沙盒隔离

- 每个会话对应独立的 `sandbox/{task_id}/`
- 任务之间的文件互不干扰
- 适合文件处理、工具执行和多任务并行场景

### 3. 流式响应

- Agent 输出支持 token 级流式返回
- API 通过 NDJSON 持续返回中间过程和最终答案
- 适合前端实时渲染和工具调用可视化

### 4. 模型工厂

- 通过 `config/model.yaml` 统一管理不同场景模型
- 支持为不同任务角色分配不同模型
- 当前默认支持 `main`、`text_generation`、`element_extraction`、`code_generation`

### 5. Tool 与 Skill 高效集成

- `tool` 适合高频、核心、强耦合能力
- `skill` 适合模块化、独立脚本、外部能力封装
- 两者都可纳入 Agent 的执行链路

### 6. 会话自主压缩

- 当上下文过长时，框架支持对历史消息做压缩处理
- 用于降低 token 成本，保持长流程可持续运行

---

## 技术栈

### 核心框架

- **Python 3.10+**：核心开发语言
- **LangChain**：Agent、消息、工具调用基础能力
- **LangChain Core / Community / OpenAI / Google GenAI**：模型接入层
- **LangGraph**：相关依赖已接入，便于后续状态图扩展

### 交互与工程化

- **Rich**：CLI 渲染、Markdown 展示、终端美化
- **Typer**：命令行入口支持
- **prompt-toolkit**：交互输入体验增强
- **PyYAML**：模型和配置文件解析
- **python-dotenv**：环境变量加载

### 服务与运行

- **http.server / ThreadingHTTPServer**：轻量 API 服务与本地静态服务
- **NDJSON**：API 流式响应格式
- **浏览器静态前端**：Copilot 工作台界面

### 模型提供商

当前项目支持接入以下主流模型源：

- **OpenAI**
- **Gemini**
- **Qwen / DashScope**
- **DeepSeek**
- **Kimi**

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/wz289494/anyclaw.git
cd anyclaw
```

### 2. 创建并激活虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows：

```bash
python -m venv venv
venv\\Scripts\\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. 配置环境变量

在项目根目录创建 `.env`：

```env
OPENAI_APIKEY=your_openai_api_key
DEEPSEEK_APIKEY=your_deepseek_api_key
QWEN_APIKEY=your_qwen_api_key
GEMINI_APIKEY=your_gemini_api_key
KIMI_APIKEY=your_kimi_api_key
```

### 5. 配置模型

编辑 `config/model.yaml`：

```yaml
main:
  provider: deepseek
  model: deepseek-chat
  api_key_env: DEEPSEEK_APIKEY

text_generation:
  provider: qwen
  model: qwen-plus
  api_key_env: QWEN_APIKEY

element_extraction:
  provider: qwen
  model: qwen-plus
  api_key_env: QWEN_APIKEY

code_generation:
  provider: deepseek
  model: deepseek-chat
  api_key_env: DEEPSEEK_APIKEY
```

---

## 使用方式

### CLI

```bash
anyclaw-cli
```

常用命令：

- `/new`：新建会话
- `/memory`：查看并恢复历史会话
- `/models`：查看模型配置
- `/tools`：查看工具列表
- `/skills`：查看 skills 列表
- `/clear`：清空 memory 与 sandbox
- `/exit`：退出 CLI

### API

```bash
anyclaw-api
```

默认地址：

```text
http://127.0.0.1:7000
```

主要接口：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/tools` | 返回工具列表 markdown |
| GET | `/api/models` | 返回模型列表 markdown |
| GET | `/api/skills` | 返回 skills 列表 markdown |
| POST | `/api/new` | 创建新会话并返回 `task_id` |
| GET | `/api/memory` | 返回全部会话 `task_id` |
| GET | `/api/session?task_id=...` | 获取指定会话消息 |
| POST | `/api/clear` | 清空 memory 与 sandbox |
| POST | `/api/agent` | 执行一次 Agent 对话，流式返回结果 |

创建会话：

```bash
curl -X POST http://127.0.0.1:7000/api/new
```

查看会话：

```bash
curl http://127.0.0.1:7000/api/memory
```

发起流式对话：

```bash
curl -N -X POST http://127.0.0.1:7000/api/agent   -H "Content-Type: application/json"   -d '{"task_id":"你的task_id","query":"你好，介绍一下你能做什么"}'
```

返回事件包括：

- `tool_call`
- `tool_result`
- `state_update`
- `final`

### Copilot

```bash
anyclaw-copilot
```

默认行为：

- 本地打开浏览器页面：`http://127.0.0.1:7001`
- 自动探测 API 是否可用
- 如果 API 未启动，尝试自动启动本地 API

---

## Agent 配置与模型建议

### 模型角色说明

| 场景 | 作用 | 建议 |
|---|---|---|
| `main` | 主流程模型，负责推理、工具调用、整体对话质量 | 选择推理能力强、工具调用稳定的模型 |
| `text_generation` | 纯文本生成 | 可选择成本更低、速度更快的模型 |
| `element_extraction` | 结构化抽取 | 选择格式稳定、遵循指令较好的模型 |
| `code_generation` | 代码生成与修复 | 选择代码能力更强的模型 |

### 主模型与简单模型的区别

| 维度 | 主模型 | 简单模型 |
|---|---|---|
| 推理能力 | 更强，适合多步任务 | 较弱，适合单步任务 |
| 工具调用能力 | 更稳定，能更好选择工具与组织参数 | 容易漏调工具或参数不准 |
| 流式输出质量 | 通常更稳定 | 通常更快但波动更大 |
| 长上下文表现 | 更好 | 一般 |
| 成本 | 更高 | 更低 |
| 适用位置 | `main` | `text_generation`、部分辅助场景 |

建议：

- `main` 尽量选择推理和工具调用能力都比较强的模型
- 辅助模型可以选择更轻、更快、更低成本的模型
- 如果你的 Agent 严重依赖工具链，请优先保证 `main` 的质量

---

## Tool 与 Skill 的区别

| 维度 | Tool | Skill |
|---|---|---|
| 本质 | 框架内注册的 Python 工具 | 标准化目录 + `SKILL.md` + 脚本能力 |
| 接入方式 | 直接注册到 Agent 工具列表 | 自动扫描 `skills/*/SKILL.md` |
| 执行方式 | 直接函数调用 | 独立脚本/子能力调用 |
| 适用场景 | 高频核心能力、需要深度接入框架内部状态 | 独立模块能力、可复用能力、文档/表格/搜索类扩展 |
| 开发成本 | 略高 | 更低，更适合快速扩展 |
| 典型示例 | 文件管理、命令执行、技能读取 | `pdf`、`xlsx` 等元技能 |

一句话理解：

- **Tool** 更像框架原生能力
- **Skill** 更像可插拔的能力包

---

## Vibe Coding SOP

如果你想把 AnyClaw 改造成自己的垂类 Agent，可以按下面的顺序来。

### 1. 先让 AI 熟悉项目

给你的 coding agent 一段清晰任务说明：

```text
先熟悉当前项目结构，重点查看：
- agent/reactagent.py
- tools/
- skills/
- config/model.yaml
- prompt/
- api/
- copilot/
```

### 2. 再做你的品牌和角色定制

通常先改这些：

- 项目名称
- Logo
- 欢迎语
- `prompt/system_prompt.txt`
- 默认模型配置
- 默认工具列表

### 3. 优先补 Tool，而不是先改大框架

推荐方式：

1. 在 `tools/` 下新增工具文件
2. 用统一输入输出格式实现工具函数
3. 在 `tools/__init__.py` 导出
4. 在 `agent/reactagent.py` 注册到 `AGENT_TOOLS`
5. 在 CLI 和 API 中实际验证工具调用效果

### 4. 需要模块化能力时再加 Skill

推荐方式：

1. 新建 `skills/my_skill/`
2. 编写 `SKILL.md`
3. 在 `scripts/` 中实现脚本
4. 保证脚本输出可解析
5. 通过 `/skills` 或 API 查看是否成功加载

---

## Skills 载入 SOP

### 标准目录结构

```text
skills/
└── my_skill/
    ├── SKILL.md
    └── scripts/
        └── my_skill.py
```

### `SKILL.md` 最少应包含

- skill 名称
- 能力说明
- 使用场景
- 脚本入口
- 输入输出约定

### 脚本建议

- 输出 JSON 或易解析文本
- 尽量幂等
- 出错时返回明确错误信息
- 文件操作尽量基于 `task_id` 对应目录进行隔离

### 测试方式

```bash
python skills/my_skill/scripts/my_skill.py
```

然后在 CLI 或 API 中验证 skill 是否被扫描到。

---

## 项目结构

```text
anyclaw/
├── agent/                 # ReAct Agent 核心
├── api/                   # HTTP API 模式
├── cli/                   # CLI 模式
├── copilot/               # 浏览器 Copilot 工作台
├── config/                # 配置文件
├── docs/                  # 图片与文档资源
├── memory/STM/            # 会话短期记忆
├── model/                 # 模型工厂
├── prompt/                # System prompt 等模板
├── sandbox/               # 会话任务隔离目录
├── skills/                # 元技能目录
├── tools/                 # 框架工具
├── utils/                 # 通用工具函数
├── scripts/               # 测试或辅助脚本
├── pyproject.toml
└── README.md
```

---

## 适合谁用

AnyClaw 适合这几类开发者：

- 想快速做一个垂类 Agent 原型的人
- 想把 Agent 能力接到现有 Web/App 里的团队
- 想保留控制权，不想被重型框架限制的人
- 想用 `tool + skill + prompt + model` 快速迭代能力的人

---

## 许可证

本项目采用 **NON-COMMERCIAL LEARNING LICENSE 1.1**。

如需商业使用，请联系版权所有者获取商业许可。完整条款请见 `LICENSE.txt`。

---

## 致谢

如果这个项目对你有帮助，欢迎 Star。
