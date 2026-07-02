# Checklist

## vector_analysis Skill
- [x] `skills/vector_analysis.py` 存在，函数 `vector_analysis(operation, **kwargs)` 实现
- [x] 用 `@arcpy_error_handler` 装饰
- [x] 入口设置 `arcpy.env.overwriteOutput = True`
- [x] 支持 operation: buffer（arcpy.analysis.Buffer）
- [x] 支持 operation: intersect（arcpy.analysis.Intersect）
- [x] 支持 operation: union（arcpy.analysis.Union）
- [x] 支持 operation: near（arcpy.analysis.Near）
- [x] 支持 operation: spatial_join（arcpy.analysis.SpatialJoin）
- [x] 支持 operation: dissolve（arcpy.management.Dissolve）
- [x] 未支持的 operation 返回 ValueError 结构化错误
- [x] 成功返回 `result` 含 `output` 键
- [x] `schemas/vector_analysis.json` 存在，含 name/description/parameters
- [x] operation 参数有 enum 列出 6 种值
- [x] 各参数 description 说明物理意义（类型/单位/可选/默认值）

## raster_analysis Skill
- [x] `skills/raster_analysis.py` 存在，函数 `raster_analysis(operation, **kwargs)` 实现
- [x] 用 `@arcpy_error_handler` 装饰
- [x] 入口设置 `arcpy.env.overwriteOutput = True`
- [x] 支持 operation: reclassify（arcpy.sa.Reclassify）
- [x] 支持 operation: raster_calculator（表达式求值）
- [x] 支持 operation: slope（arcpy.sa.Slope）
- [x] 支持 operation: aspect（arcpy.sa.Aspect）
- [x] 支持 operation: contour（arcpy.sa.Contour）
- [x] 未支持的 operation 返回 ValueError 结构化错误
- [x] 成功返回 `result` 含 `output` 键
- [x] `schemas/raster_analysis.json` 存在，含 name/description/parameters
- [x] operation 参数有 enum 列出 5 种值

## interpolation Skill
- [x] `skills/interpolation.py` 存在，函数 `interpolation(operation, **kwargs)` 实现
- [x] 用 `@arcpy_error_handler` 装饰
- [x] 入口设置 `arcpy.env.overwriteOutput = True`
- [x] 支持 operation: idw（arcpy.sa.Idw）
- [x] 支持 operation: kriging（arcpy.sa.Kriging）
- [x] 支持 operation: spline（arcpy.sa.Spline）
- [x] 支持 operation: natural_neighbor（arcpy.sa.NaturalNeighbor）
- [x] 未支持的 operation 返回 ValueError 结构化错误
- [x] 成功返回 `result` 含 `output` 键
- [x] `schemas/interpolation.json` 存在，含 name/description/parameters
- [x] operation 参数有 enum 列出 4 种值

## spatial_statistics Skill
- [x] `skills/spatial_statistics.py` 存在，函数 `spatial_statistics(operation, **kwargs)` 实现
- [x] 用 `@arcpy_error_handler` 装饰
- [x] 入口设置 `arcpy.env.overwriteOutput = True`
- [x] 支持 operation: kernel_density（arcpy.sa.KernelDensity）
- [x] 支持 operation: point_density（arcpy.sa.PointDensity）
- [x] 支持 operation: zonal_statistics（arcpy.sa.ZonalStatisticsAsTable）
- [x] 支持 operation: hot_spot_analysis（arcpy.stats.HotSpots）
- [x] 支持 operation: summary_statistics（arcpy.analysis.Statistics）
- [x] 未支持的 operation 返回 ValueError 结构化错误
- [x] 成功返回 `result` 含 `output` 键
- [x] `schemas/spatial_statistics.json` 存在，含 name/description/parameters
- [x] operation 参数有 enum 列出 5 种值

## 双交付物与一致性
- [x] 每个 Skill 同时存在 schema json 与 py 文件
- [x] schema name 与函数名一一对应
- [x] 顶层字段为 `parameters`（与 execute_arcpy_code 一致）
- [x] 所有函数返回结构化 dict（{success, result, messages, error}）

## 文档更新
- [x] README 已实现 Skill 一览表新增 4 个工具箱
- [x] README 目录结构图已更新
