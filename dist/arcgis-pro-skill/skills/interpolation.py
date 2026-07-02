"""插值分析工具箱 Skill 执行函数。

通过 operation 参数路由到具体的插值方法（IDW、克里金、样条函数、自然邻域），
将离散点要素插值为连续栅格表面，并保存到指定输出路径。
所有插值方法均基于 arcpy.sa（Spatial Analyst）实现。
"""
import arcpy

from core.errors import arcpy_error_handler, make_success, make_error
from arcpy.sa import *


@arcpy_error_handler
def interpolation(operation, **kwargs):
    """插值分析工具箱，根据 operation 参数分派到具体插值方法。

    支持的 operation：
        - idw: 反距离权重插值（Inverse Distance Weighted）
        - kriging: 克里金插值（基于半变异函数的地统计插值）
        - spline: 样条函数插值（REGULARIZED/TENSION）
        - natural_neighbor: 自然邻域插值

    通用必需参数（kwargs）：
        in_point_features: 输入点要素类路径
        z_field: 插值字段名（要插值的数值字段，如高程、浓度）
        out_raster: 输出栅格路径

    各方法特有的可选参数详见对应分支注释。

    Args:
        operation: 插值方法类型，枚举 idw/kriging/spline/natural_neighbor
        **kwargs: 其余参数，按 operation 不同分别消费

    Returns:
        通过 make_success/make_error 包装的返回结构；
        成功时 result.output 为输出栅格路径，并附带 operation 与原始 params。
    """
    # 函数入口第一行设置覆盖输出，避免输出已存在时报错
    arcpy.env.overwriteOutput = True

    # 公共必需参数：输入点要素、插值字段、输出栅格路径
    in_point_features = kwargs.get("in_point_features")
    z_field = kwargs.get("z_field")
    out_raster = kwargs.get("out_raster")

    if operation == "idw":
        # IDW 反距离权重插值：距离越近的点权重越大，权重按距离的 power 次方衰减
        # cell_size 不传时由 arcpy 从环境或输入推断
        cell_size = kwargs.get("cell_size")
        power = kwargs.get("power", 2)
        search_radius = kwargs.get("search_radius")
        out = arcpy.sa.Idw(in_point_features, z_field, cell_size, power, search_radius)
        out.save(out_raster)
        return make_success({"output": out_raster, "operation": operation, "params": kwargs})

    elif operation == "kriging":
        # 克里金插值：基于半变异函数的地统计方法，提供无偏最优估计
        # semi_variogram 默认 Spherical，可选 Spherical/Circular/Exponential/Gaussian/Linear
        semi_variogram = kwargs.get("semi_variogram", "Spherical")
        cell_size = kwargs.get("cell_size")
        search_radius = kwargs.get("search_radius")
        out = arcpy.sa.Kriging(in_point_features, z_field, semi_variogram, cell_size, search_radius)
        out.save(out_raster)
        return make_success({"output": out_raster, "operation": operation, "params": kwargs})

    elif operation == "spline":
        # 样条函数插值：通过数学曲面拟合点，产生平滑表面
        # method 默认 REGULARIZED（可选 TENSION），weight 默认 0.1，number_points 默认 12
        cell_size = kwargs.get("cell_size")
        method = kwargs.get("method", "REGULARIZED")
        weight = kwargs.get("weight", 0.1)
        number_points = kwargs.get("number_points", 12)
        out = arcpy.sa.Spline(in_point_features, z_field, cell_size, method, weight, number_points)
        out.save(out_raster)
        return make_success({"output": out_raster, "operation": operation, "params": kwargs})

    elif operation == "natural_neighbor":
        # 自然邻域插值：基于 Voronoi 图的局部插值，边界平滑且不产生异常振荡
        # 仅需 cell_size 可选参数
        cell_size = kwargs.get("cell_size")
        out = arcpy.sa.NaturalNeighbor(in_point_features, z_field, cell_size)
        out.save(out_raster)
        return make_success({"output": out_raster, "operation": operation, "params": kwargs})

    else:
        # 未支持的 operation，返回明确的错误信息与可选值列表
        return make_error(
            "ValueError",
            f"不支持的 operation: {operation}，支持的 operation: idw/kriging/spline/natural_neighbor",
        )
