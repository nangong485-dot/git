# Tasks

- [x] Task 1: 搭建框架基础目录结构
  - [x] SubTask 1.1: 创建 `skills/`、`schemas/`、`core/` 目录
  - [x] SubTask 1.2: 在 `core/errors.py` 实现统一返回格式构造器（`make_success`、`make_error`）与 `arcpy.ExecuteError` 捕获装饰器

- [x] Task 2: 实现上下文感知工具 `get_arcgis_context`
  - [x] SubTask 2.1: 在 `core/context.py` 编写 `get_arcgis_context()` 函数，返回活动 aprx 路径、活动地图名、工作空间、坐标系等
  - [x] SubTask 2.2: 在 `schemas/get_arcgis_context.json` 编写 JSON Schema 工具声明（含清晰描述）

- [x] Task 3: 实现环境设置工具 `set_arcgis_environment`
  - [x] SubTask 3.1: 在 `skills/set_arcgis_environment.py` 编写函数，支持设置 workspace、coordinate_system、extent、cell_size、overwriteOutput 等
  - [x] SubTask 3.2: 在 `schemas/set_arcgis_environment.json` 编写 JSON Schema 工具声明

- [x] Task 4: 实现通用执行器 `execute_arcpy_code`（底层兜底）
  - [x] SubTask 4.1: 在 `core/executor.py` 编写 `execute_arcpy_code(code)`，受控执行 Python 脚本字符串，捕获 `arcpy.ExecuteError` 与通用异常，结构化返回
  - [x] SubTask 4.2: 在 `schemas/execute_arcpy_code.json` 编写 JSON Schema 工具声明，明确兜底场景与参数约束

- [x] Task 5: 编写框架使用说明（README 片段，置于仓库根目录或 docs/）
  - [x] SubTask 5.1: 说明双层架构、Skill 双交付物规范、统一返回格式、新增 Skill 的步骤

# Task Dependencies
- Task 2、Task 3、Task 4 均依赖 Task 1（统一返回格式与目录结构）
- Task 4（通用执行器）可与 Task 2、Task 3 并行实现
- Task 5 依赖 Task 1~4 全部完成
