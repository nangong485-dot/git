# 数据与工程管理 Skill Spec

## Why
现有工具箱覆盖了空间分析、地图排版，但缺少对地理数据库（GDB）、要素类（Feature Class）、栅格数据集的 CRUD 管理能力。用户需要通过 Skill 创建 GDB、列出/创建/复制/删除/重命名/描述要素类与栅格数据集，形成完整的「数据管理 → 分析 → 制图」链路。注意：工程上下文获取已由 `get_arcgis_context` Skill 提供，本 Skill 聚焦于数据集管理操作，避免重复。

## What Changes
- 新增 **`data_management`** 顶层工具箱 Skill，通过 `operation` 参数选择具体数据管理操作。
- 支持的 operation（共 10 种）：
  - 数据库管理：`create_gdb`、`compact_gdb`
  - 数据集列举：`list_feature_classes`、`list_rasters`、`list_tables`
  - 数据集 CRUD：`create_feature_class`、`copy_data`、`delete_data`、`rename_data`、`describe_data`
- 产出双交付物：`schemas/data_management.json` + `skills/data_management.py`
- 主要调用 `arcpy.management` 与 `arcpy.Describe`，对 GDB 中的要素类与栅格做增删改查。
- 基于已有 `@arcpy_error_handler` 装饰器与 `make_success`/`make_error` 统一返回格式。

## Impact
- Affected specs: `setup-arcgispro-skill-framework`（复用 core/errors.py）
- Affected code:
  - `skills/data_management.py`（新增）
  - `schemas/data_management.json`（新增）
  - `README.md`（更新已实现 Skill 一览表与目录结构）

## ADDED Requirements

### Requirement: data_management Skill（数据与工程管理工具箱）
系统 SHALL 提供一个名为 `data_management` 的 Skill，通过 `operation` 参数选择数据管理操作。

#### Scenario: 创建地理数据库
- **WHEN** 模型调用 `data_management(operation="create_gdb", out_folder_path=<目录>, gdb_name=<名称>)`
- **THEN** 调用 `arcpy.management.CreateFileGDB`，返回 GDB 完整路径
- **WHEN** 模型调用 `data_management(operation="compact_gdb", gdb_path=<GDB路径>)`
- **THEN** 调用 `arcpy.management.Compact`，压缩 GDB，返回成功信息

#### Scenario: 列出数据集
- **WHEN** 模型调用 `data_management(operation="list_feature_classes", workspace=<工作空间>)`
- **THEN** 调用 `arcpy.ListDatasets` / `arcpy.ListFeatureClasses`，返回要素类名称列表
- **WHEN** 模型调用 `data_management(operation="list_rasters", workspace=<工作空间>)`
- **THEN** 返回栅格数据集名称列表
- **WHEN** 模型调用 `data_management(operation="list_tables", workspace=<工作空间>)`
- **THEN** 返回表名称列表

#### Scenario: 创建要素类
- **WHEN** 模型调用 `data_management(operation="create_feature_class", out_path=<GDB路径>, out_name=<名称>, geometry_type="POINT", spatial_reference=<可选WKID或路径>, fields=<可选字段列表>)`
- **THEN** 调用 `arcpy.management.CreateFeatureclass`，可选添加字段，返回要素类完整路径

#### Scenario: 复制/删除/重命名数据
- **WHEN** 模型调用 `data_management(operation="copy_data", in_data=<路径>, out_data=<路径>)`
- **THEN** 调用 `arcpy.management.Copy`，返回输出路径
- **WHEN** 模型调用 `data_management(operation="delete_data", in_data=<路径>)`
- **THEN** 调用 `arcpy.management.Delete`，返回成功信息
- **WHEN** 模型调用 `data_management(operation="rename_data", in_data=<路径>, out_data=<新名称>)`
- **THEN** 调用 `arcpy.management.Rename`，返回输出路径

#### Scenario: 描述数据集
- **WHEN** 模型调用 `data_management(operation="describe_data", in_data=<路径>)`
- **THEN** 调用 `arcpy.Describe`，返回数据集类型、名称、路径、空间参考、字段列表（若是要素类）、波段数（若是栅格）等元信息

### Requirement: 工作空间处理规范
data_management Skill 操作数据集时 SHALL：
- 接受 `workspace` 参数（GDB 路径或文件夹路径），用于列举操作
- 列举操作前调用 `arcpy.env.workspace = workspace` 设置当前工作空间，操作完成后恢复原值
- 列举操作可选 `dataset_type` 过滤（如 Point/Polygon/Polyline 仅对 list_feature_classes 有意义）

#### Scenario: 列举时设置工作空间
- **WHEN** 调用 list_* 操作
- **THEN** 先备份 `arcpy.env.workspace`，设置为新 workspace，列举后恢复原值

### Requirement: 返回结构
data_management Skill SHALL 返回结构化 dict，成功时 `result` 字段至少包含 `operation` 以及 operation 特定的输出信息。

#### Scenario: 成功返回
- **WHEN** 任一 operation 执行成功
- **THEN** 返回 `{"success": True, "result": {"operation": op, ...}, "messages": [...], "error": None}`

### Requirement: 稳健性
data_management Skill SHALL：
- 使用 `@arcpy_error_handler` 装饰
- 入口设置 `arcpy.env.overwriteOutput = True`
- 未支持的 operation 返回 `make_error("ValueError", ...)`
- 必填参数缺失时返回结构化错误
