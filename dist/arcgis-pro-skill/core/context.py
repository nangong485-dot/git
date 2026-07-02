"""上下文感知工具：获取当前 ArcGIS Pro 会话的关键上下文信息。"""
import arcpy

from core.errors import arcpy_error_handler, make_success


@arcpy_error_handler
def get_arcgis_context():
    """返回当前 ArcGIS Pro 会话的上下文信息。

    收集活动工程（aprx）路径、活动地图名称、当前工作空间、scratch 工作空间、
    输出坐标系、处理范围、像元大小以及 overwriteOutput 等关键环境信息，
    供调用方在执行 GIS 任务前了解当前会话状态。

    Returns:
        dict: 通过 make_success 包装的返回结构，result 字段为包含以下键的字典：
            - aprx_path (str|None): 当前活动工程路径
            - active_map (str|None): 活动地图名称
            - workspace (str|None): 当前工作空间
            - scratch_workspace (str|None): scratch 工作空间
            - coordinate_system (str|None): 输出坐标系（WKT 或名称）
            - extent (str|None): 处理范围
            - cell_size (str|None): 像元大小
            - overwrite_output (bool): 是否允许覆盖输出
    """
    # 活动工程路径与活动地图：若当前无活动工程会抛 RuntimeError，单独捕获不中断整体返回
    aprx_path = None
    active_map = None
    try:
        # 通过 "CURRENT" 关键字获取当前活动的 ArcGIS Pro 工程
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprx_path = aprx.filePath
        # activeMap 获取单独 try，无活动地图时设为 None
        try:
            active_map = aprx.activeMap.name
        except Exception:
            # 无活动地图或读取失败，置为 None
            active_map = None
    except RuntimeError:
        # 无活动工程，aprx_path 与 active_map 均保持 None
        aprx_path = None
        active_map = None

    # 其他 env 字段直接读取，可能为 None
    context = {
        "aprx_path": aprx_path,
        "active_map": active_map,
        "workspace": arcpy.env.workspace,
        "scratch_workspace": arcpy.env.scratchWorkspace,
        "coordinate_system": arcpy.env.outputCoordinateSystem,
        "extent": str(arcpy.env.extent) if arcpy.env.extent is not None else None,
        "cell_size": arcpy.env.cellSize,
        "overwrite_output": bool(arcpy.env.overwriteOutput),
    }

    return make_success(context)
