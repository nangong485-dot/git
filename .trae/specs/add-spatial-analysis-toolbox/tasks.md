# Tasks

- [x] Task 1: 实现 `vector_analysis` Skill（矢量分析工具箱）
  - [x] SubTask 1.1: 在 `skills/vector_analysis.py` 编写 `vector_analysis(operation, **kwargs)`，支持 buffer/intersect/union/near/spatial_join/dissolve，用 `@arcpy_error_handler` 装饰，入口设置 overwriteOutput=True
  - [x] SubTask 1.2: 在 `schemas/vector_analysis.json` 编写 JSON Schema（parameters 格式），operation 枚举 6 种，参数定义清晰

- [x] Task 2: 实现 `raster_analysis` Skill（栅格分析工具箱）
  - [x] SubTask 2.1: 在 `skills/raster_analysis.py` 编写 `raster_analysis(operation, **kwargs)`，支持 reclassify/raster_calculator/slope/aspect/contour
  - [x] SubTask 2.2: 在 `schemas/raster_analysis.json` 编写 JSON Schema

- [x] Task 3: 实现 `interpolation` Skill（插值分析工具箱）
  - [x] SubTask 3.1: 在 `skills/interpolation.py` 编写 `interpolation(operation, **kwargs)`，支持 idw/kriging/spline/natural_neighbor
  - [x] SubTask 3.2: 在 `schemas/interpolation.json` 编写 JSON Schema

- [x] Task 4: 实现 `spatial_statistics` Skill（空间统计工具箱）
  - [x] SubTask 4.1: 在 `skills/spatial_statistics.py` 编写 `spatial_statistics(operation, **kwargs)`，支持 kernel_density/point_density/zonal_statistics/hot_spot_analysis/summary_statistics
  - [x] SubTask 4.2: 在 `schemas/spatial_statistics.json` 编写 JSON Schema

- [x] Task 5: 更新 README 与框架文档
  - [x] SubTask 5.1: 在 `README.md` 已实现 Skill 一览表新增 4 个工具箱 Skill
  - [x] SubTask 5.2: 更新目录结构图

# Task Dependencies
- Task 1、2、3、4 相互独立，可并行实现（均依赖 core/errors.py，已就绪）
- Task 5 依赖 Task 1~4 完成
