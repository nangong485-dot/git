---
name: ArcGIS Pro 自动化
description: 操作 ArcGIS Pro 工程文件（.aprx），执行空间分析、数据管理、地图排版与出图等 GIS 任务。当用户提到 ArcGIS、ArcPy、空间分析、栅格处理、要素类、地理数据库、地图排版、导出图片/PDF 等 GIS 相关任务时触发。
---

# ArcGIS Pro 自动化技能

## 描述

本技能封装了 ArcGIS Pro 常用的自动化操作，让你能够通过调用 Python 函数来完成 GIS 数据处理、空间分析、地图排版与出图等任务。所有函数均基于 `arcpy` 实现，运行环境为 ArcGIS Pro 的 `arcgispro-py3` Python 环境。

## 使用场景

当用户提出以下类型的需求时，使用本技能：

- **空间分析**：缓冲区、叠加分析、插值、栅格计算、密度分析、热点分析等
- **数据管理**：创建 GDB、管理要素类与栅格、复制/删除/重命名数据、查看数据元信息
- **地图排版**：操作 .aprx 工程、管理图层、调整地图范围、更新标题与图例
- **出图导出**：将布局导出为 PDF / PNG / JPEG / TIFF
- **环境设置**：设置工作空间、坐标系、像元大小、范围等
- **上下文获取**：查看当前工程中的地图、布局、工作空间等信息

## 运行环境要求

- 所有代码必须在 **`arcgispro-py3`** 环境中执行（ArcGIS Pro 自带的 conda 环境）
- 需要 `arcpy` 模块（仅在 ArcGIS Pro Python 环境中可用）
- 本地必须安装 ArcGIS Pro（3.x 版本）

## 工具清单

本技能包含 9 个工具函数，按用途分为以下类别：

### 基础设施

| 工具 | 用途 |
|------|------|
| `get_arcgis_context` | 获取当前活动工程/地图/工作空间/坐标系等上下文信息 |
| `set_arcgis_environment` | 设置工作空间、坐标系、范围、像元大小、overwriteOutput 等环境变量 |
| `execute_arcpy_code` | 通用 ArcPy 脚本执行器（兜底工具，运行自定义 Python/ArcPy 脚本） |

### 空间分析工具箱

| 工具 | 支持的 operation |
|------|-----------------|
| `vector_analysis` | buffer / intersect / union / near / spatial_join / dissolve |
| `raster_analysis` | reclassify / raster_calculator / slope / aspect / contour |
| `interpolation` | idw / kriging / spline / natural_neighbor |
| `spatial_statistics` | kernel_density / point_density / zonal_statistics / hot_spot_analysis / summary_statistics |

### 地图排版与出图工具箱

| 工具 | 支持的 operation |
|------|-----------------|
| `map_layout` | list_maps / list_layouts / add_layer / remove_layer / set_layer_visibility / set_map_extent / zoom_to_layer / update_title / update_legend / export_layout |

### 数据管理工具箱

| 工具 | 支持的 operation |
|------|-----------------|
| `data_management` | create_gdb / compact_gdb / list_feature_classes / list_rasters / list_tables / create_feature_class / copy_data / delete_data / rename_data / describe_data |

## 调用方式

### 方式一：直接调用工具函数（推荐）

对于有对应专属工具的任务，直接调用对应的 Python 函数。函数定义在项目根目录的 `skills/` 和 `core/` 文件夹中。

**调用步骤：**

1. 从 `skills/` 或 `core/` 导入对应函数
2. 传入参数执行
3. 解析返回结果

**示例：执行缓冲区分析**

```python
import sys
sys.path.insert(0, r"C:\path\to\workspace")

from skills.vector_analysis import vector_analysis

result = vector_analysis(
    operation="buffer",
    input_features=r"C:\data\roads.shp",
    output_features=r"C:\data\roads_buffer.shp",
    distance="50 Meters"
)

print(result)
```

**示例：导出布局为 PDF**

```python
import sys
sys.path.insert(0, r"C:\path\to\workspace")

from skills.map_layout import map_layout

result = map_layout(
    operation="export_layout",
    aprx_path=r"C:\project\map.aprx",
    layout_name="Layout",
    output_path=r"C:\output\map.pdf",
    format="PDF",
    resolution=300
)

print(result)
```

### 方式二：使用 execute_arcpy_code 兜底

当任务比较复杂（多步骤组合、自定义逻辑）且没有对应专属工具时，使用 `execute_arcpy_code` 函数执行自定义脚本。

**编码规则（必须遵守）：**

1. **基础设置**：始终在代码开头包含 `import arcpy`
2. **环境覆盖**：始终包含 `arcpy.env.overwriteOutput = True`
3. **输出打印**：通过 `print()` 输出关键执行节点和最终结果路径
4. **错误处理**：使用 `try...except`，专门捕获 `arcpy.ExecuteError`
5. **路径规范**：使用原始字符串（如 `r"C:\data\map.aprx"`）或正斜杠
6. **独立运行**：每次传入的代码必须是自包含的完整脚本

**示例：**

```python
import sys
sys.path.insert(0, r"C:\path\to\workspace")

from core.executor import execute_arcpy_code

code = """
import arcpy
import sys

try:
    arcpy.env.overwriteOutput = True
    input_fc = r"C:/temp/data.gdb/roads"
    output_fc = r"C:/temp/data.gdb/roads_buffer"

    print(f"开始执行缓冲区分析：{input_fc}")
    arcpy.analysis.Buffer(input_fc, output_fc, "50 Meters")
    print(f"SUCCESS: 缓冲区分析完成，结果保存在 {output_fc}")

except arcpy.ExecuteError:
    print("ARCPY ERROR:\\n" + arcpy.GetMessages(2))
except Exception as e:
    print(f"PYTHON ERROR: {str(e)}")
"""

output = execute_arcpy_code(code)
print(output)
```

## 返回值格式

### 专属工具函数（结构化 dict）

所有专属工具（get_arcgis_context 除外的工具箱 Skill）返回统一结构：

```python
{
    "success": True/False,
    "result": {...},      # 成功时为结果数据，失败时为 None
    "messages": [...],    # 执行过程中的消息（如 GP 工具消息）
    "error": None         # 失败时为 {"type": "...", "message": "..."}
}
```

### execute_arcpy_code（字符串）

返回脚本的标准输出（stdout + stderr），成功时为 print 输出，失败时包含错误堆栈。

## 函数定义位置

所有工具函数的源代码位于项目根目录：

```
workspace/
├── core/
│   ├── errors.py           # 统一返回格式 + 错误处理装饰器
│   ├── context.py          # get_arcgis_context 实现
│   └── executor.py         # execute_arcpy_code 实现
├── skills/
│   ├── set_arcgis_environment.py
│   ├── vector_analysis.py
│   ├── raster_analysis.py
│   ├── interpolation.py
│   ├── spatial_statistics.py
│   ├── map_layout.py
│   └── data_management.py
├── schemas/                # JSON Schema 工具声明
└── prompts/                # 系统提示词（execute_arcpy_code 的 Coding Rules）
```

## 注意事项

1. **优先使用专属工具**：当任务有对应的原子化工具时，优先调用专属工具而非 `execute_arcpy_code`。专属工具参数明确、错误处理更聚焦。
2. **环境切换**：确保执行 Python 代码的环境是 `arcgispro-py3`，而非系统默认 Python。
3. **路径处理**：所有文件路径使用原始字符串（`r"..."`）或正斜杠，避免转义问题。
4. **数据覆盖**：所有工具函数已默认设置 `arcpy.env.overwriteOutput = True`，输出会覆盖已有数据。
5. **工程保存**：`map_layout` 中修改工程的操作会自动调用 `aprx.save()`，只读操作（list/export）不会保存。
6. **工作空间恢复**：`data_management` 的列举操作会自动备份并恢复 `arcpy.env.workspace`，不会污染外部环境。

## 详细文档

每个工具的详细参数说明和使用方法，请参考对应的源文件和 Schema 定义（位于 `schemas/` 目录下的 JSON 文件）。
