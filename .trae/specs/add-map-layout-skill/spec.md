# 地图排版与出图 Skill Spec

## Why
现有工具箱覆盖了矢量/栅格/插值/空间统计分析，但缺少地图排版（Layout）与出图能力。用户需要通过 Skill 操作 .aprx 工程文件中的地图（Maps）、布局（Layouts），调整地图范围、图例、标题等元素，并导出为图片或 PDF，形成完整的「数据处理 → 制图输出」闭环。

## What Changes
- 新增 **`map_layout`** 顶层工具箱 Skill，通过 `operation` 参数选择具体排版/出图操作。
- 支持的 operation（共 10 种）：
  - 工程与地图管理：`list_maps`、`list_layouts`
  - 图层管理：`add_layer`、`remove_layer`、`set_layer_visibility`
  - 地图范围：`set_map_extent`、`zoom_to_layer`
  - 布局元素：`update_title`、`update_legend`
  - 导出：`export_layout`（支持 PDF / PNG / JPEG / TIFF）
- 产出双交付物：`schemas/map_layout.json` + `skills/map_layout.py`
- 使用 `arcpy.mp` 模块操作 .aprx 工程，所有修改保存回工程文件。
- 基于已有 `@arcpy_error_handler` 装饰器与 `make_success`/`make_error` 统一返回格式。

## Impact
- Affected specs: `setup-arcgispro-skill-framework`（复用 core/errors.py）
- Affected code:
  - `skills/map_layout.py`（新增）
  - `schemas/map_layout.json`（新增）
  - `README.md`（更新已实现 Skill 一览表与目录结构）

## ADDED Requirements

### Requirement: map_layout Skill（地图排版与出图工具箱）
系统 SHALL 提供一个名为 `map_layout` 的 Skill，通过 `operation` 参数选择排版/出图操作，调用 `arcpy.mp` 操作 .aprx 工程。

#### Scenario: 列出地图与布局
- **WHEN** 模型调用 `map_layout(operation="list_maps", aprx_path=<路径>)`
- **THEN** 返回工程中所有地图的名称列表
- **WHEN** 模型调用 `map_layout(operation="list_layouts", aprx_path=<路径>)`
- **THEN** 返回工程中所有布局的名称列表

#### Scenario: 图层管理
- **WHEN** 模型调用 `map_layout(operation="add_layer", aprx_path=<路径>, map_name=<地图名>, layer_path=<图层路径>)`
- **THEN** 向指定地图添加图层，返回成功信息与图层名
- **WHEN** 模型调用 `map_layout(operation="remove_layer", aprx_path=<路径>, map_name=<地图名>, layer_name=<图层名>)`
- **THEN** 从指定地图移除图层，返回成功信息
- **WHEN** 模型调用 `map_layout(operation="set_layer_visibility", aprx_path=<路径>, map_name=<地图名>, layer_name=<图层名>, visible=True/False)`
- **THEN** 设置指定图层的可见性，返回成功信息

#### Scenario: 地图范围
- **WHEN** 模型调用 `map_layout(operation="set_map_extent", aprx_path=<路径>, map_name=<地图名>, layout_name=<布局名>, extent="XMin YMin XMax YMax")`
- **THEN** 设置布局中地图框的范围为指定矩形，返回成功信息
- **WHEN** 模型调用 `map_layout(operation="zoom_to_layer", aprx_path=<路径>, map_name=<地图名>, layout_name=<布局名>, layer_name=<图层名>)`
- **THEN** 将地图框范围缩放至指定图层全图，返回成功信息

#### Scenario: 布局元素
- **WHEN** 模型调用 `map_layout(operation="update_title", aprx_path=<路径>, layout_name=<布局名>, title_text=<新标题>, title_element_name=<可选>)`
- **THEN** 修改布局中标题文本元素的文字，返回成功信息
- **WHEN** 模型调用 `map_layout(operation="update_legend", aprx_path=<路径>, layout_name=<布局名>, legend_element_name=<可选>, visible_layers=[...])`
- **THEN** 更新图例显示的图层列表，返回成功信息

#### Scenario: 导出布局
- **WHEN** 模型调用 `map_layout(operation="export_layout", aprx_path=<路径>, layout_name=<布局名>, output_path=<输出路径>, format="PDF", resolution=300)`
- **THEN** 将布局导出为指定格式（支持 PDF / PNG / JPEG / TIFF），返回输出文件路径
- 支持参数：resolution（DPI，默认 300）、format（默认 PDF）
- 注：导出 PDF 用 `layout.exportToPDF`，导出图片用对应的 `exportToPNG` / `exportToJPEG` / `exportToTIFF`

### Requirement: 工程文件操作规范
map_layout Skill 操作 .aprx 工程时 SHALL：
- 使用 `arcpy.mp.ArcGISProject(aprx_path)` 打开工程（不用 "CURRENT"，因为脚本可能独立运行）
- 所有修改完成后调用 `aprx.save()` 保存
- 对于修改操作，先保存原始值以便异常时回滚（或至少捕获异常确保不损坏工程）
- aprx_path 参数必填，明确指定操作哪个工程

#### Scenario: 工程保存
- **WHEN** 调用任何修改工程的 operation
- **THEN** 操作成功后调用 aprx.save()，并在返回信息中说明已保存

### Requirement: 返回结构
map_layout Skill SHALL 返回结构化 dict，成功时 `result` 字段至少包含 `operation`、`aprx_path` 以及 operation 特定的输出信息。

#### Scenario: 成功返回
- **WHEN** 任一 operation 执行成功
- **THEN** 返回 `{"success": True, "result": {"operation": op, "aprx_path": path, ...}, "messages": [...], "error": None}`

### Requirement: 稳健性
map_layout Skill SHALL：
- 使用 `@arcpy_error_handler` 装饰
- 入口设置 `arcpy.env.overwriteOutput = True`
- 未支持的 operation 返回 `make_error("ValueError", ...)`
- 工程打开失败（如路径不存在）时捕获异常并结构化返回
