# Checklist

## 框架基础
- [x] 框架目录结构（`skills/`、`schemas/`、`core/`）已建立
- [x] `core/errors.py` 提供统一返回格式构造器 `make_success(result, messages)` 与 `make_error(error_type, message, messages)`
- [x] `core/errors.py` 提供可复用的异常捕获装饰器，显式捕获 `arcpy.ExecuteError` 并提取 `arcpy.GetMessages()`

## 双交付物规范
- [x] 每个已实现的 Skill 同时存在 JSON Schema 文件与 Python 执行函数
- [x] JSON Schema 包含 `name`、`description`、`input_schema` 三个字段
- [x] Python 函数与 Schema 通过命名约定一一对应

## 通用执行器 execute_arcpy_code
- [x] 接收 `code`（字符串）参数，在 arcgispro-py3 环境执行
- [x] 捕获 `arcpy.ExecuteError`，结构化返回 GP 工具错误消息
- [x] 捕获通用 `Exception`，返回语法/运行时错误信息，不导致进程崩溃
- [x] 执行前显式设置 `arcpy.env.overwriteOutput = True`
- [x] Schema 描述明确说明：仅当无对应原子化 Skill 时才调用此兜底工具

## 上下文感知 get_arcgis_context
- [x] 返回活动工程（.aprx）路径
- [x] 返回活动地图（Map）名称
- [x] 返回当前工作空间（workspace）
- [x] 返回默认坐标系（coordinate system）
- [x] 异常时仍返回结构化错误，不抛出未捕获异常

## 环境设置 set_arcgis_environment
- [x] 支持设置 `workspace`
- [x] 支持设置 `coordinate_system`
- [x] 支持设置 `extent`（处理范围）
- [x] 支持设置 `cell_size`（像元大小）
- [x] 支持设置 `overwriteOutput`
- [x] 设置完成后返回当前环境快照
- [x] 所有可选参数未传入时保持原值不变

## 稳健性与环境释放标准
- [x] 所有底层 ArcPy 函数使用 `try...except` 结构
- [x] 显式捕获 `arcpy.ExecuteError`
- [x] 涉及覆盖数据时设置 `arcpy.env.overwriteOutput = True`
- [x] 使用 `memory`/`in_memory` 的函数在结束/异常分支清理临时图层

## 描述清晰度
- [x] 每个 Schema 的 `description` 说明适用场景
- [x] 每个 Schema 的 `description` 说明何时不该调用（如适用）
- [x] 每个参数的 `description` 说明物理意义（类型/单位/坐标系/可选/默认值）

## 统一返回格式
- [x] 成功返回包含 `success=True`、`result`、`messages`、`error=None`
- [x] 失败返回包含 `success=False`、`result=None`、`messages`、`error={"type","message"}`
- [x] 所有 Skill 函数遵循该返回格式
