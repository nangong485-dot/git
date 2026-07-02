# ArcGIS Pro Skill 开发框架

让大模型（Claude）通过标准化 Skill 接口驱动本地 ArcGIS Pro（arcgispro-py3 环境）完成 GIS 任务。

## 1. 双层架构

本框架采用「顶层原子化高频工具 + 底层通用执行器兜底」的双层架构，在调用准确性与灵活性之间取得平衡。

- **顶层（原子化高频工具）**：针对特定 GIS 任务设计专属 Skill，参数明确、语义清晰，降低模型调用出错率。已实现：`get_arcgis_context`、`set_arcgis_environment`。
- **底层（通用执行器兜底）**：`execute_arcpy_code`，接收完整 Python 脚本字符串，用于复杂自定义 ArcPy 逻辑。
- **优先级**：高频任务优先调用原子化 Skill；仅当无对应专属 Skill 时才用 `execute_arcpy_code`。

## 2. 双交付物规范

每个 Skill 必须同时产出两份交付物，缺一不可：

- **JSON Schema 工具声明**（`schemas/<skill_name>.json`）：含 `name`、`description`、`input_schema`
- **Python 执行函数**（`skills/<skill_name>.py` 或 `core/<skill_name>.py`）：对应实现

两者通过命名约定一一对应（同名）。Schema 声明面向大模型，决定「能否被调用」；Python 函数面向本地执行环境，决定「如何执行」。

## 3. 统一返回格式

所有 Skill 函数返回统一字典结构，便于模型解析与上层编排：

- 成功：
  ```python
  {"success": True, "result": ..., "messages": [...], "error": None}
  ```
- 失败：
  ```python
  {"success": False, "result": None, "messages": [...], "error": {"type": "...", "message": "..."}}
  ```

其中 `messages` 记录执行过程中的提示信息（如 GP 工具消息），`error` 在失败时携带错误类型与可读消息。

## 4. 开发强制标准

新增或维护 Skill 时必须满足以下标准：

- **稳健性**：所有底层 ArcPy 函数用 `@arcpy_error_handler` 装饰，自动捕获 `arcpy.ExecuteError` 与 `Exception`，统一转换为失败返回结构。
- **环境释放**：涉及覆盖数据或 `memory` 工作空间时，设置 `arcpy.env.overwriteOutput = True`，并在执行完成后清理临时图层，避免残留影响后续任务。
- **描述清晰**：Schema 的 `description` 须说明适用场景、不应调用场景、各参数物理意义（类型 / 单位 / 坐标系 / 可选 / 默认值），供模型准确决策。

## 5. 已实现 Skill 一览

| Skill 名 | 类型 | 位置 | 说明 |
|----------|------|------|------|
| `get_arcgis_context` | 顶层原子化 | `core/context.py` | 获取当前活动工程 / 地图 / 工作空间 / 坐标系等上下文 |
| `set_arcgis_environment` | 顶层原子化 | `skills/set_arcgis_environment.py` | 设置工作空间、坐标系、范围、像元大小、`overwriteOutput` 等 |
| `execute_arcpy_code` | 底层兜底 | `core/executor.py` | 通用 ArcPy 脚本执行器，接收完整 Python 脚本字符串 |

## 6. 新增 Skill 的步骤

按以下顺序执行：

1. **判定归属**：确定该任务属于顶层原子化 Skill 还是底层兜底（复杂多步骤逻辑走兜底）。
2. **编写执行函数**：在 `skills/`（或 `core/`）下创建 `<skill_name>.py`，实现执行函数，用 `@arcpy_error_handler` 装饰，返回 `make_success` / `make_error`。
3. **编写 Schema 声明**：在 `schemas/` 下创建 `<skill_name>.json`，编写 `name` / `description` / `input_schema`，`description` 须说明适用场景、不应调用场景、参数物理意义。
4. **处理环境副作用**：若涉及覆盖数据或 `memory` 工作空间，在函数内设置 `arcpy.env.overwriteOutput = True` 并清理临时图层。
5. **验证**：双交付物齐全、返回格式统一、错误处理完整、描述清晰。

## 7. 目录结构

```
/workspace
├── core/                          # 框架基础设施
│   ├── __init__.py
│   ├── errors.py                  # 统一返回格式 + arcpy.ExecuteError 捕获装饰器
│   ├── context.py                 # get_arcgis_context 实现
│   └── executor.py                # execute_arcpy_code 通用执行器实现
├── skills/                        # 顶层原子化 Skill 的 Python 执行函数
│   ├── __init__.py
│   └── set_arcgis_environment.py  # set_arcgis_environment 实现
└── schemas/                       # 各 Skill 的 JSON Schema 工具声明
    ├── execute_arcpy_code.json
    ├── get_arcgis_context.json
    └── set_arcgis_environment.json
```

约定：

- `core/` 存放框架基础设施（统一错误处理、上下文、通用执行器）。
- `skills/` 存放顶层原子化 Skill 的 Python 实现。
- `schemas/` 存放所有 Skill 的 JSON Schema 工具声明。

## 8. 运行环境

- **Python 环境**：`arcgispro-py3`（ArcGIS Pro 自带 conda 环境）。
- **依赖**：`arcpy`（仅在该环境可用，标准 Python 环境无法安装）。
- **调用方**：大模型通过 Schema 声明调用对应函数，函数在本地 `arcgispro-py3` 环境执行，结果以统一返回格式回传给模型。
