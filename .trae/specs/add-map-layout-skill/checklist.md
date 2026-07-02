# Checklist

## map_layout Skill
- [x] `skills/map_layout.py` 存在，函数 `map_layout(operation, **kwargs)` 实现
- [x] 用 `@arcpy_error_handler` 装饰
- [x] 入口设置 `arcpy.env.overwriteOutput = True`
- [x] 支持 operation: list_maps（返回工程中所有地图名称列表）
- [x] 支持 operation: list_layouts（返回工程中所有布局名称列表）
- [x] 支持 operation: add_layer（向指定地图添加图层）
- [x] 支持 operation: remove_layer（从指定地图移除图层）
- [x] 支持 operation: set_layer_visibility（设置图层可见性）
- [x] 支持 operation: set_map_extent（设置布局中地图框范围）
- [x] 支持 operation: zoom_to_layer（缩放地图框到图层全图）
- [x] 支持 operation: update_title（修改布局标题文本）
- [x] 支持 operation: update_legend（更新图例显示图层）
- [x] 支持 operation: export_layout（导出布局为 PDF/PNG/JPEG/TIFF）
- [x] 所有修改工程的 operation 调用 `aprx.save()` 保存
- [x] 未支持的 operation 返回 `make_error("ValueError", ...)`
- [x] 成功返回 `result` 含 `operation`、`aprx_path` 键
- [x] `schemas/map_layout.json` 存在，含 name/description/parameters
- [x] operation 参数有 enum 列出 10 种值
- [x] 各参数 description 说明物理意义（类型/单位/可选/默认值）

## 双交付物与一致性
- [x] 同时存在 schema json 与 py 文件
- [x] schema name 与函数名一致（map_layout）
- [x] 顶层字段为 `parameters`（不是 input_schema）
- [x] 函数返回结构化 dict（通过 make_success/make_error）

## 文档更新
- [x] README 已实现 Skill 一览表新增 map_layout
- [x] README 目录结构图已更新
