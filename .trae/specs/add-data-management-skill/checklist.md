# Checklist

## data_management Skill
- [x] `skills/data_management.py` 存在，函数 `data_management(operation, **kwargs)` 实现
- [x] 用 `@arcpy_error_handler` 装饰
- [x] 入口设置 `arcpy.env.overwriteOutput = True`
- [x] 支持 operation: create_gdb（arcpy.management.CreateFileGDB）
- [x] 支持 operation: compact_gdb（arcpy.management.Compact）
- [x] 支持 operation: list_feature_classes（arcpy.ListFeatureClasses 或 ListDatasets）
- [x] 支持 operation: list_rasters（arcpy.ListRasters）
- [x] 支持 operation: list_tables（arcpy.ListTables）
- [x] 支持 operation: create_feature_class（arcpy.management.CreateFeatureclass）
- [x] 支持 operation: copy_data（arcpy.management.Copy）
- [x] 支持 operation: delete_data（arcpy.management.Delete）
- [x] 支持 operation: rename_data（arcpy.management.Rename）
- [x] 支持 operation: describe_data（arcpy.Describe）
- [x] 列举操作前设置 workspace，操作后恢复原值
- [x] 未支持的 operation 返回 `make_error("ValueError", ...)`
- [x] 成功返回 `result` 含 `operation` 键
- [x] `schemas/data_management.json` 存在，含 name/description/parameters
- [x] operation 参数有 enum 列出 10 种值
- [x] 各参数 description 说明物理意义（类型/单位/可选/默认值）

## 双交付物与一致性
- [x] 同时存在 schema json 与 py 文件
- [x] schema name 与函数名一致（data_management）
- [x] 顶层字段为 `parameters`（不是 input_schema）
- [x] 函数返回结构化 dict（通过 make_success/make_error）

## 文档更新
- [x] README 已实现 Skill 一览表新增 data_management
- [x] README 目录结构图已更新
