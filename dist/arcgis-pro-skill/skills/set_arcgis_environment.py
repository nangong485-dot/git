"""设置 ArcPy 运行环境的 Skill 执行函数。

允许在执行 GP 工具前统一设置 ArcPy 运行环境（工作空间、输出坐标系、
处理范围、像元大小、overwriteOutput、捕捉栅格、掩膜、TIN 保存区域），
并返回设置后的环境快照供模型确认。
所有参数均为可选，未传入（None）时保持原值不变。
"""
import arcpy

from core.errors import arcpy_error_handler, make_success


@arcpy_error_handler
def set_arcgis_environment(
    workspace=None,
    coordinate_system=None,
    extent=None,
    cell_size=None,
    overwrite_output=None,
    snap_raster=None,
    mask=None,
    tin_save_area=None
):
    """设置 ArcPy 运行环境，并返回设置后的环境快照。

    所有参数可选；传入 None 表示不修改该项，保持当前值不变。
    仅当参数非 None 时才执行对应的赋值操作。

    Args:
        workspace: 当前工作空间路径。地理数据库（.gdb）或文件夹路径，
            作为后续 GP 工具的默认输入/输出位置。
        coordinate_system: 输出坐标系。可为 WKT 字符串、坐标系名称
            （如 "WGS 1984 UTM Zone 50N"）或 .prj 文件路径。
        extent: 处理范围。字符串形式，如 "XMin YMin XMax YMax"，
            或图层路径（取图层范围）。
        cell_size: 输出像元大小。数值或字符串，单位与输出坐标系一致
            （如米、度）。
        overwrite_output: 是否允许覆盖已有输出。布尔值，会强制转换为 bool。
        snap_raster: 捕捉栅格路径。用于对齐输出栅格像元，确保与参考栅格
            像元边界一致。
        mask: 掩膜栅格或要素路径。限制 GP 工具仅处理掩膜覆盖范围内的像元。
        tin_save_area: TIN 保存区域。用于 TIN 相关工具的处理范围约束。

    Returns:
        通过 make_success 包装的环境快照字典，包含 workspace、
        coordinate_system、extent、cell_size、overwrite_output、
        snap_raster、mask、tin_save_area 八项当前值。
    """
    # 仅当参数非 None 时才执行赋值，保持其他环境项原值不变
    if workspace is not None:
        arcpy.env.workspace = workspace

    if coordinate_system is not None:
        # outputCoordinateSystem 接受 WKT 字符串、坐标系名称或 .prj 路径
        arcpy.env.outputCoordinateSystem = coordinate_system

    if extent is not None:
        # extent 接受 "XMin YMin XMax YMax" 字符串或图层路径
        arcpy.env.extent = extent

    if cell_size is not None:
        # cellSize 接受数值或字符串，单位与输出坐标系一致
        arcpy.env.cellSize = cell_size

    if overwrite_output is not None:
        # 强制转换为布尔值，避免传入非布尔类型导致歧义
        arcpy.env.overwriteOutput = bool(overwrite_output)

    if snap_raster is not None:
        arcpy.env.snapRaster = snap_raster

    if mask is not None:
        arcpy.env.mask = mask

    if tin_save_area is not None:
        arcpy.env.tinSaveArea = tin_save_area

    # 构造当前环境快照：outputCoordinateSystem 与 extent 为对象时转为字符串
    snapshot = {
        "workspace": arcpy.env.workspace,
        "coordinate_system": str(arcpy.env.outputCoordinateSystem) if arcpy.env.outputCoordinateSystem else None,
        "extent": str(arcpy.env.extent) if arcpy.env.extent else None,
        "cell_size": arcpy.env.cellSize,
        "overwrite_output": arcpy.env.overwriteOutput,
        "snap_raster": arcpy.env.snapRaster,
        "mask": arcpy.env.mask,
        "tin_save_area": arcpy.env.tinSaveArea,
    }

    return make_success(snapshot)
