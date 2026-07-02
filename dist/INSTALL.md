# ArcGIS Pro 自动化 Skill — 安装与使用指南

## 包内容

```
arcgis-pro-skill/
├── SKILL.md                 # 技能入口（Trae 自动读取）
├── core/                    # 基础设施（3 个）
│   ├── errors.py            # 统一返回格式 + 错误处理装饰器
│   ├── context.py           # get_arcgis_context
│   └── executor.py          # execute_arcpy_code
├── skills/                  # 工具箱（6 个）
│   ├── set_arcgis_environment.py
│   ├── vector_analysis.py
│   ├── raster_analysis.py
│   ├── interpolation.py
│   ├── spatial_statistics.py
│   ├── map_layout.py
│   └── data_management.py
├── schemas/                 # JSON Schema 工具声明（9 个）
├── prompts/                 # 系统提示词
│   └── execute_arcpy_code.md
└── reference/               # 参考文档
    └── FRAMEWORK_README.md  # 框架完整文档
```

**工具总数：9 个工具函数，共 50 种 operation**

## 安装方式

### 方式一：ZIP 导入（推荐）

1. 打开 Trae IDE
2. 进入 **设置 → 技能（Skills）**
3. 点击 **导入** 按钮
4. 选择 `arcgis-pro-skill.zip` 文件
5. 完成导入

### 方式二：手动放置到项目目录

将 `arcgis-pro-skill/` 文件夹放入项目的 `.trae/skills/` 目录：

```
你的项目/
├── .trae/
│   └── skills/
│       └── arcgis-pro-skill/   ← 放在这里
│           └── SKILL.md
├── 你的代码...
```

然后在 Trae 中打开该项目，Skill 会自动生效。

### 方式三：设置为全局 Skill

如果你希望所有项目都能用这个 Skill：

1. 先按方式二放入某个项目
2. 在 Trae 的 **设置 → 技能** 中找到该技能
3. 点击右侧齿轮图标，选择 **应用到全局**

全局 Skill 存放路径：
- **Windows**：`%userprofile%/.trae-cn/skills/`
- **macOS/Linux**：`~/.trae-cn/skills/`

## 使用前置条件

1. **安装 ArcGIS Pro 3.x**
2. **启用 arcgispro-py3 环境**：
   - 打开 ArcGIS Pro → 工程 → 包管理器 → 环境
   - 确认 `arcgispro-py3` 环境存在且包含 `arcpy`
   - 建议克隆一份环境用于开发，避免污染默认环境
3. **Trae Python 解释器切换**：
   - 在 Trae 中设置 Python 解释器为 `arcgispro-py3` 的路径
   - Windows 默认路径：`C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe`

## 使用方式

### 触发 Skill

在 Trae 对话中直接描述你的 GIS 需求即可，例如：

| 场景 | 你可以说 |
|------|----------|
| 创建 GDB | "帮我在 D 盘 data 目录下创建一个叫 project 的文件地理数据库" |
| 缓冲区分析 | "给 roads.shp 做一个 200 米的缓冲区，结果放到 data.gdb 里" |
| 插值 | "用克里金方法对 sampling 点的 elevation 字段做插值，像元大小 30 米" |
| 热点分析 | "对犯罪数据做热点分析，用 count 字段" |
| 出图 | "把项目里的 Layout1 导出成 300DPI 的 PDF 到桌面" |
| 数据管理 | "查看一下 data.gdb 里有哪些要素类" |
| 自定义脚本 | "用 execute_arcpy_code 跑一个自定义的栅格计算" |

### 可用工具一览

| 类别 | 工具 | Operation 数量 |
|------|------|---------------|
| 基础设施 | get_arcgis_context | - |
| | set_arcgis_environment | - |
| | execute_arcpy_code（兜底） | - |
| 矢量分析 | vector_analysis | 6（buffer/intersect/union/near/spatial_join/dissolve） |
| 栅格分析 | raster_analysis | 5（reclassify/raster_calculator/slope/aspect/contour） |
| 插值分析 | interpolation | 4（idw/kriging/spline/natural_neighbor） |
| 空间统计 | spatial_statistics | 5（kernel_density/point_density/zonal_statistics/hot_spot_analysis/summary_statistics） |
| 地图排版 | map_layout | 10（list_maps/list_layouts/add_layer/remove_layer/set_layer_visibility/set_map_extent/zoom_to_layer/update_title/update_legend/export_layout） |
| 数据管理 | data_management | 10（create_gdb/compact_gdb/list_feature_classes/list_rasters/list_tables/create_feature_class/copy_data/delete_data/rename_data/describe_data） |

## 注意事项

1. **Python 环境**：必须在 `arcgispro-py3` 环境中运行，标准 Python 环境无法 `import arcpy`
2. **路径格式**：所有文件路径建议使用原始字符串（`r"C:\path\to\data"`）或正斜杠（`"C:/path/to/data"`）
3. **数据覆盖**：所有工具默认设置 `arcpy.env.overwriteOutput = True`，输出会覆盖同名文件
4. **优先使用专属工具**：有对应专属工具时不要用 `execute_arcpy_code` 兜底，专属工具参数更明确、错误处理更好

## 版本信息

- 兼容 ArcGIS Pro 版本：3.0+
- Skill 版本：1.0
- 工具总数：9 个工具函数，50 种 operation
