# 空间分析与空间统计工具箱 Spec

## Why
框架基础设施（execute_arcpy_code、get_arcgis_context、set_arcgis_environment）已就绪，但缺少面向具体 GIS 任务的高频原子化 Skill。用户需要一组覆盖矢量分析、栅格分析、插值分析、空间统计四大类的常用工具箱 Skill，让模型能直接调用结构化接口完成常见空间分析与统计任务，而不必每次通过通用执行器编写完整脚本。

## What Changes
- 新增 4 个顶层原子化 Skill（每类一个），均通过 `operation` 参数选择具体工具：
  - **`vector_analysis`**：矢量分析工具箱。支持 buffer / intersect / union / near / spatial_join / dissolve。
  - **`raster_analysis`**：栅格分析工具箱。支持 reclassify / raster_calculator / slope / aspect / contour。
  - **`interpolation`**：插值分析工具箱。支持 idw / kriging / spline / natural_neighbor。
  - **`spatial_statistics`**：空间统计工具箱。支持 kernel_density / point_density / zonal_statistics / hot_spot_analysis / summary_statistics。
- 每个 Skill 产出双交付物：`schemas/<skill>.json`（parameters 格式）+ `skills/<skill>.py`（执行函数）。
- 所有 Skill 函数用 `@arcpy_error_handler` 装饰，返回结构化 dict（`{success, result, messages, error}`）。
- 涉及覆盖输出时设置 `arcpy.env.overwriteOutput = True`。
- Schema 描述遵循「Schema 与系统提示词分离」原则：`description` 简短，复杂约束另放 `prompts/`。

## Impact
- Affected specs: `setup-arcgispro-skill-framework`（复用其 core/errors.py 的 make_success/make_error/arcpy_error_handler）
- Affected code:
  - `skills/vector_analysis.py`（新增）
  - `skills/raster_analysis.py`（新增）
  - `skills/interpolation.py`（新增）
  - `skills/spatial_statistics.py`（新增）
  - `schemas/vector_analysis.json`（新增）
  - `schemas/raster_analysis.json`（新增）
  - `schemas/interpolation.json`（新增）
  - `schemas/spatial_statistics.json`（新增）
  - `README.md`（更新已实现 Skill 一览表）

## ADDED Requirements

### Requirement: vector_analysis Skill（矢量分析工具箱）
系统 SHALL 提供一个名为 `vector_analysis` 的 Skill，通过 `operation` 参数选择矢量分析工具，完成缓冲区、叠加、近邻、空间连接、融合等操作。

#### Scenario: 缓冲区分析
- **WHEN** 模型调用 `vector_analysis(operation="buffer", input_features=<路径>, output_features=<路径>, distance=<距离+单位>)`
- **THEN** 执行 `arcpy.analysis.Buffer`，返回结构化结果包含输出要素类路径

#### Scenario: 相交分析
- **WHEN** 模型调用 `vector_analysis(operation="intersect", input_features=[fc1, fc2], output_features=<路径>)`
- **THEN** 执行 `arcpy.analysis.Intersect`，返回输出要素类路径

#### Scenario: 近邻分析
- **WHEN** 模型调用 `vector_analysis(operation="near", input_features=<路径>, near_features=<路径>, distance=<可选>)`
- **THEN** 执行 `arcpy.analysis.Near`，在输入要素属性表添加 NEAR_FID/NEAR_DIST 字段，返回处理消息

#### Scenario: 未知 operation
- **WHEN** 模型传入未支持的 operation 值
- **THEN** 返回 `{"success": False, "error": {"type": "ValueError", "message": "不支持的 operation: <值>，支持的 operation: buffer/intersect/union/near/spatial_join/dissolve"}}`

### Requirement: raster_analysis Skill（栅格分析工具箱）
系统 SHALL 提供一个名为 `raster_analysis` 的 Skill，通过 `operation` 参数选择栅格分析工具。

#### Scenario: 栅格重分类
- **WHEN** 模型调用 `raster_analysis(operation="reclassify", in_raster=<路径>, reclass_fields=<字段>, remap=<重映射>, out_raster=<路径>)`
- **THEN** 执行 `arcpy.sa.Reclassify`，返回输出栅格路径

#### Scenario: 坡度计算
- **WHEN** 模型调用 `raster_analysis(operation="slope", in_raster=<DEM路径>, out_raster=<路径>, output_unit="DEGREE")`
- **THEN** 执行 `arcpy.sa.Slope`，返回输出栅格路径

#### Scenario: 栅格计算器表达式执行
- **WHEN** 模型调用 `raster_analysis(operation="raster_calculator", expression=<表达式>, output_raster=<路径>)`
- **THEN** 执行 `arcpy.sa.RasterCalculator` 或等效表达式求值，返回输出栅格路径

### Requirement: interpolation Skill（插值分析工具箱）
系统 SHALL 提供一个名为 `interpolation` 的 Skill，通过 `operation` 参数选择插值方法。

#### Scenario: IDW 插值
- **WHEN** 模型调用 `interpolation(operation="idw", in_point_features=<路径>, z_field=<字段>, out_raster=<路径>, cell_size=<像元大小>, power=2)`
- **THEN** 执行 `arcpy.sa.Idw`，返回输出栅格路径

#### Scenario: 克里金插值
- **WHEN** 模型调用 `interpolation(operation="kriging", in_point_features=<路径>, z_field=<字段>, out_raster=<路径>, semi_variogram=<模型>, cell_size=<像元大小>)`
- **THEN** 执行 `arcpy.sa.Kriging`，返回输出栅格路径

#### Scenario: 样条函数插值
- **WHEN** 模型调用 `interpolation(operation="spline", in_point_features=<路径>, z_field=<字段>, out_raster=<路径>, method="REGULARIZED")`
- **THEN** 执行 `arcpy.sa.Spline`，返回输出栅格路径

### Requirement: spatial_statistics Skill（空间统计工具箱）
系统 SHALL 提供一个名为 `spatial_statistics` 的 Skill，通过 `operation` 参数选择空间统计工具。

#### Scenario: 核密度估计
- **WHEN** 模型调用 `spatial_statistics(operation="kernel_density", in_features=<路径>, population_field=<字段>, out_raster=<路径>, cell_size=<像元大小>, search_radius=<半径>)`
- **THEN** 执行 `arcpy.sa.KernelDensity`，返回输出栅格路径

#### Scenario: 区域统计
- **WHEN** 模型调用 `spatial_statistics(operation="zonal_statistics", in_zone_data=<路径>, zone_field=<字段>, in_value_raster=<路径>, out_table=<路径>, statistics_type="MEAN")`
- **THEN** 执行 `arcpy.sa.ZonalStatisticsAsTable`，返回输出表路径

#### Scenario: 热点分析 (Getis-Ord Gi*)
- **WHEN** 模型调用 `spatial_statistics(operation="hot_spot_analysis", input_features=<路径>, input_field=<字段>, output_features=<路径>, conceptualization_of_spatial_relationships="INVERSE_DISTANCE")`
- **THEN** 执行 `arcpy.stats.HotSpots`，返回输出要素类路径与 Gi ZScore/PValue 字段说明

#### Scenario: 汇总统计
- **WHEN** 模型调用 `spatial_statistics(operation="summary_statistics", in_table=<路径>, out_table=<路径>, statistics_fields=[[field, "SUM"], ...], case_field=<可选>)`
- **THEN** 执行 `arcpy.analysis.Statistics`，返回输出表路径

### Requirement: 统一的 operation 路由模式
每个工具箱 Skill SHALL 使用统一的 operation 路由模式：函数内部根据 `operation` 值分派到对应的 arcpy 调用，未支持的 operation 返回结构化错误。

#### Scenario: operation 路由
- **WHEN** 调用任一工具箱 Skill
- **THEN** 函数读取 operation 参数，匹配支持的子操作列表，匹配成功则调用对应 arcpy 工具，否则返回 ValueError 错误结构

### Requirement: 返回结果包含输出路径
所有工具箱 Skill 的成功返回 `result` 字段 SHALL 至少包含 `output` 键（输出数据路径），便于模型在后续步骤引用。

#### Scenario: 成功返回包含 output
- **WHEN** 任一工具箱 Skill 执行成功
- **THEN** 返回 `{"success": True, "result": {"output": "<输出路径>", "operation": "<op>", ...}, "messages": [...], "error": None}`

### Requirement: 环境覆盖保护
所有工具箱 Skill SHALL 在函数入口设置 `arcpy.env.overwriteOutput = True`，确保输出可覆盖。

#### Scenario: 覆盖输出
- **WHEN** 调用任一工具箱 Skill 且输出路径已存在
- **THEN** 因 overwriteOutput=True，工具覆盖已有输出执行成功
