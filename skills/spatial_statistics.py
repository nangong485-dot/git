"""空间统计工具箱 Skill 执行函数。

通过 operation 参数路由到具体的空间统计工具，包括：
- kernel_density：核密度估计（arcpy.sa.KernelDensity）
- point_density：点密度估计（arcpy.sa.PointDensity）
- zonal_statistics：区域统计（arcpy.sa.ZonalStatisticsAsTable）
- hot_spot_analysis：热点分析 Getis-Ord Gi*（arcpy.stats.HotSpots）
- summary_statistics：汇总统计（arcpy.analysis.Statistics）

所有分支均通过 @arcpy_error_handler 统一捕获 arcpy.ExecuteError，
成功返回 make_success 包装的结构化字典（包含 output 路径、operation、params）。
"""
import arcpy
from arcpy.sa import *

from core.errors import arcpy_error_handler, make_success, make_error


@arcpy_error_handler
def spatial_statistics(operation, **kwargs):
    """空间统计工具箱入口，按 operation 分派到具体工具。

    通用约定：
        - 必需参数缺失由 arcpy 工具自身抛错，被 @arcpy_error_handler 捕获。
        - 涉及输出的工具在入口统一设置 arcpy.env.overwriteOutput = True。
        - 成功返回 result 至少包含 output（输出路径）、operation、params 三项。

    Args:
        operation (str): 空间统计类型，可选值：
            kernel_density / point_density / zonal_statistics /
            hot_spot_analysis / summary_statistics
        **kwargs: 各 operation 对应的参数，详见各分支注释。

    Returns:
        通过 make_success / make_error 包装的结构化返回值。
    """
    # 函数入口统一允许覆盖已有输出，避免输出已存在时报错
    arcpy.env.overwriteOutput = True

    # 1. 核密度估计：用每个点周围的搜索半径生成平滑密度面
    if operation == "kernel_density":
        # 必需参数：in_features（输入要素）、out_raster（输出栅格）
        # population_field 默认 "NONE"，表示每点计 1
        # cell_size / search_radius 可选，未传 None 由 arcpy 默认处理
        in_features = kwargs.get("in_features")
        out_raster = kwargs.get("out_raster")
        population_field = kwargs.get("population_field", "NONE")
        cell_size = kwargs.get("cell_size")
        search_radius = kwargs.get("search_radius")
        area_unit = kwargs.get("area_unit", "SQUARE_KILOMETERS")
        out = arcpy.sa.KernelDensity(
            in_features, population_field, cell_size, search_radius, area_unit
        )
        out.save(out_raster)
        return make_success({"output": out_raster, "operation": operation, "params": kwargs})

    # 2. 点密度估计：在邻域内统计点数（或人口字段）生成密度栅格
    elif operation == "point_density":
        # 必需参数：in_features（输入要素）、out_raster（输出栅格）
        # neighborhood 默认 None 由 arcpy 自动选择 Circle
        in_features = kwargs.get("in_features")
        out_raster = kwargs.get("out_raster")
        population_field = kwargs.get("population_field", "NONE")
        cell_size = kwargs.get("cell_size")
        neighborhood = kwargs.get("neighborhood")
        area_unit = kwargs.get("area_unit", "SQUARE_KILOMETERS")
        out = arcpy.sa.PointDensity(
            in_features, population_field, cell_size, neighborhood, area_unit
        )
        out.save(out_raster)
        return make_success({"output": out_raster, "operation": operation, "params": kwargs})

    # 3. 区域统计：对每个分区汇总值栅格的统计量，输出为表
    elif operation == "zonal_statistics":
        # 必需参数：in_zone_data、zone_field、in_value_raster、out_table
        # statistics_type 默认 "ALL"，可选 MEAN/MAJORITY/MAXIMUM/MEDIAN/MINIMUM/
        # MINORITY/RANGE/STD/SUM/VARIETY/ALL
        in_zone_data = kwargs.get("in_zone_data")
        zone_field = kwargs.get("zone_field")
        in_value_raster = kwargs.get("in_value_raster")
        out_table = kwargs.get("out_table")
        statistics_type = kwargs.get("statistics_type", "ALL")
        arcpy.sa.ZonalStatisticsAsTable(
            in_zone_data, zone_field, in_value_raster, out_table, "DATA", statistics_type
        )
        return make_success({"output": out_table, "operation": operation, "params": kwargs})

    # 4. 热点分析（Getis-Ord Gi*）：识别空间聚集的高值（热点）/低值（冷点）区域
    elif operation == "hot_spot_analysis":
        # 必需参数：input_features、input_field、output_features
        # conceptualization_of_spatial_relationships 默认 "INVERSE_DISTANCE"
        # distance_method 默认 "EUCLIDEAN_DISTANCE"
        input_features = kwargs.get("input_features")
        input_field = kwargs.get("input_field")
        output_features = kwargs.get("output_features")
        conceptualization = kwargs.get(
            "conceptualization_of_spatial_relationships", "INVERSE_DISTANCE"
        )
        distance_method = kwargs.get("distance_method", "EUCLIDEAN_DISTANCE")
        arcpy.stats.HotSpots(
            input_features, input_field, output_features, conceptualization, distance_method
        )
        # 输出要素含 GiZScore、GiPValue 字段；附说明便于解读结果
        result = {
            "output": output_features,
            "operation": "hot_spot_analysis",
            "params": kwargs,
            "note": "输出要素含 GiZScore、GiPValue 字段；ZScore>1.96 且 PValue<0.05 为热点，ZScore<-1.96 为冷点",
        }
        return make_success(result)

    # 5. 汇总统计：按统计字段（列表的列表）聚合，可选按 case_field 分组
    elif operation == "summary_statistics":
        # 必需参数：in_table、out_table、statistics_fields
        # statistics_fields 格式：[["字段名","统计类型"], ...]，统计类型如 SUM/MEAN/MIN/MAX/STD
        # case_field 可选，支持字符串或列表
        in_table = kwargs.get("in_table")
        out_table = kwargs.get("out_table")
        statistics_fields = kwargs.get("statistics_fields")
        case_field = kwargs.get("case_field")
        if case_field is None:
            arcpy.analysis.Statistics(in_table, out_table, statistics_fields)
        else:
            arcpy.analysis.Statistics(in_table, out_table, statistics_fields, case_field)
        return make_success({"output": out_table, "operation": operation, "params": kwargs})

    # 未支持的 operation，返回结构化错误
    else:
        return make_error(
            "ValueError",
            f"不支持的 operation: {operation}，支持的 operation: "
            f"kernel_density/point_density/zonal_statistics/hot_spot_analysis/summary_statistics",
        )
