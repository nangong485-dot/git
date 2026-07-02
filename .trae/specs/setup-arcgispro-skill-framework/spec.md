# ArcGIS Pro Skill 开发框架 Spec

## Why
为了让大模型（Claude）能够稳定、可控地驱动本地 ArcGIS Pro（arcgispro-py3 环境）完成 GIS 任务，需要建立一套统一的 Skill 开发框架。该框架定义「Skill 接口（JSON Schema）+ 底层 ArcPy 执行代码」的双交付物标准，并通过「原子化高频工具 + 通用执行器兜底」的双层架构，降低模型调用出错率，同时保留对复杂自定义脚本的支持能力。

## What Changes
- 建立统一的 Skill 交付物规范：每个 Skill 必须同时产出 (1) 符合大模型调用标准的 JSON Schema 工具声明，(2) 在 arcgispro-py3 中实际运行的 Python/ArcPy 函数。
- 建立双层架构原则：
  - **顶层（原子化高频工具）**：针对特定 GIS 任务（克里金插值、栅格重分类、自动出图、环境设置等）设计专属 Skill，参数明确、语义清晰。
  - **底层（通用执行器兜底）**：提供 `execute_arcpy_code` 通用 Skill，允许运行复杂的自定义 ArcPy 脚本。
- 建立上下文感知机制：Skill 设计与实现须考虑当前活动工程（.aprx）、活动地图（Map）、当前工作空间（Workspace）。
- 建立开发强制标准：稳健性（try...except 捕获 `arcpy.ExecuteError`）、环境释放（`arcpy.env.overwriteOutput = True`、清理 `memory` 工作空间）、描述清晰（Description 明确调用场景与参数物理意义）。
- 作为框架基础设施，先行实现：
  - `execute_arcpy_code`：通用 ArcPy 执行器（底层兜底）。
  - `get_arcgis_context`：获取当前活动工程/地图/工作空间上下文（顶层原子工具）。
  - `set_arcgis_environment`：设置 ArcPy 运行环境（顶层原子工具）。

## Impact
- Affected specs: 无（首个 spec，作为后续所有 ArcGIS Pro Skill 开发的基线框架）。
- Affected code: 
  - `skills/` 目录：存放各 Skill 的 Python 执行函数（按 Skill 分文件或分模块）。
  - `schemas/` 目录：存放各 Skill 的 JSON Schema 工具声明。
  - `core/context.py`：上下文感知工具的底层实现。
  - `core/executor.py`：通用执行器的底层实现。
  - `core/errors.py`：统一的错误处理与返回格式。

## ADDED Requirements

### Requirement: 双层 Skill 架构
系统 SHALL 采用双层架构组织所有 ArcGIS Pro Skill：顶层为针对具体 GIS 任务的原子化专属 Skill，底层为 `execute_arcpy_code` 通用执行器作为兜底。

#### Scenario: 高频任务走原子化工具
- **WHEN** 模型需要完成一个已定义的高频 GIS 任务（如克里金插值）
- **THEN** 模型调用对应的专属原子化 Skill，而非通用执行器

#### Scenario: 复杂自定义脚本走通用执行器
- **WHEN** 模型需要运行未封装为原子化 Skill 的复杂 ArcPy 逻辑
- **THEN** 模型调用 `execute_arcpy_code`，传入完整的 Python 脚本字符串执行

### Requirement: 双交付物规范
每个 Skill SHALL 同时产出两份交付物：(1) JSON Schema 工具声明（含 name、description、input_schema）；(2) 对应的 Python/ArcPy 执行函数。两者通过函数名或约定键一一对应。

#### Scenario: 交付物完整性校验
- **WHEN** 新增一个 Skill
- **THEN** 必须同时提供 JSON Schema 声明文件和 Python 执行函数，缺一不可

### Requirement: 通用 ArcPy 执行器（execute_arcpy_code）
系统 SHALL 提供一个名为 `execute_arcpy_code` 的兜底 Skill，接收一段 Python 脚本字符串，在 arcgispro-py3 环境中以受控方式执行，并返回执行结果或错误信息。

#### Scenario: 正常执行自定义脚本
- **WHEN** 模型传入语法正确、逻辑完整的 ArcPy 脚本
- **THEN** 执行器在本地环境运行脚本，返回标准输出与执行状态

#### Scenario: 脚本执行出错
- **WHEN** 传入的脚本抛出异常（含 `arcpy.ExecuteError`）
- **THEN** 执行器捕获异常，将完整错误信息（含 GP 工具错误消息）结构化返回给模型，不导致进程崩溃

### Requirement: 上下文感知工具（get_arcgis_context）
系统 SHALL 提供一个名为 `get_arcgis_context` 的 Skill，返回当前 ArcGIS Pro 会话的关键上下文信息，包括活动工程路径、活动地图名称、当前工作空间、默认坐标系等。

#### Scenario: 获取上下文
- **WHEN** 模型在执行任务前需要了解当前环境
- **THEN** 调用该 Skill，返回包含 aprx 路径、活动地图、工作空间、坐标系的 JSON 结构

### Requirement: 环境设置工具（set_arcgis_environment）
系统 SHALL 提供一个名为 `set_arcgis_environment` 的 Skill，允许模型设置 ArcPy 运行环境变量（如工作空间、坐标系、处理范围、像元大小、overwriteOutput 等）。

#### Scenario: 设置工作空间与覆盖输出
- **WHEN** 模型传入 workspace 路径与 overwriteOutput=True
- **THEN** 该工具设置 `arcpy.env.workspace` 与 `arcpy.env.overwriteOutput`，并返回设置后的环境快照

### Requirement: 稳健的错误处理
所有底层 ArcPy 执行代码 SHALL 使用 `try...except` 结构，并显式捕获 `arcpy.ExecuteError`，确保 GP 工具错误信息能完整、结构化地返回给大模型。

#### Scenario: GP 工具执行失败
- **WHEN** ArcPy GP 工具执行失败抛出 `arcpy.ExecuteError`
- **THEN** 代码捕获该异常，提取 `arcpy.GetMessages()` 返回给模型，返回结构包含 success=False 与错误详情

### Requirement: 环境释放与覆盖保护
涉及覆盖现有数据或使用临时内存工作空间（`in_memory` / `memory`）的 Skill，SHALL 在执行前显式设置 `arcpy.env.overwriteOutput = True`，并在任务完成后清理临时内存图层。

#### Scenario: 使用内存工作空间
- **WHEN** Skill 中间产物写入 `memory` 工作空间
- **THEN** 代码设置 overwriteOutput=True，并在流程结束或异常分支中调用 `arcpy.management.Delete` 清理内存图层

### Requirement: 清晰的 Skill 描述
每个 Skill 的 JSON Schema 描述 SHALL 明确说明：(1) 适用场景；(2) 何时不应该调用；(3) 每个参数的物理意义（字段类型、单位、坐标系、是否可选、默认值）。

#### Scenario: 描述可读性校验
- **WHEN** 审查一个 Skill 的 JSON Schema
- **THEN** description 字段包含调用场景说明，每个参数的 description 说明其物理意义与单位

### Requirement: 统一的返回格式
所有 Skill 的 Python 执行函数 SHALL 返回统一的字典结构，至少包含 `success`（布尔）、`result`（结果数据或消息）、`messages`（GP 工具消息列表）、`error`（错误详情，失败时填充）字段。

#### Scenario: 成功返回
- **WHEN** Skill 执行成功
- **THEN** 返回 `{"success": True, "result": ..., "messages": [...], "error": None}`

#### Scenario: 失败返回
- **WHEN** Skill 执行失败
- **THEN** 返回 `{"success": False, "result": None, "messages": [...], "error": {"type": "...", "message": "..."}}`
