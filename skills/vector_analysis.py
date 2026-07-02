"""矢量分析工具箱 Skill 执行函数。

通过 operation 参数选择具体的矢量分析工具，统一路由到对应的 arcpy 工具。
支持的 operation：
  - buffer：缓冲区分析。必需参数 input_features、output_features、distance
    （形如 "50 Meters" / "100 Kilometers"）。可选 line_side、line_end_type、
    dissolve_option、dissolve_field、method。
  - intersect：相交分析。必需参数 input_features（要素类列表）、output_features。
    可选 join_attributes、cluster_tolerance、output_type。
  - union：联合分析。必需参数 input_features（要素类列表）、output_features。
    可选 join_attributes、cluster_tolerance、gaps。
  - near：近邻分析。必需参数 input_features、near_features。可选 search_radius、
    location、angle、method。近邻信息写入输入要素属性表，返回 input_features。
  - spatial_join：空间连接。必需参数 target_features、join_features、output_features。
    可选 join_operation、join_type、field_mapping、match_option、search_radius、
    distance_field_name。
  - dissolve：融合。必需参数 input_features、output_features。可选 dissolve_fields
    （列表）、statistics_fields、multi_part、unsplit_lines。

所有分支成功后返回 make_success({"output": <输出路径>, "operation": operation,
"params": kwargs})；未支持的 operation 返回 make_error。
"""
import arcpy

from core.errors import arcpy_error_handler, make_success, make_error


@arcpy_error_handler
def vector_analysis(operation, **kwargs):
    """矢量分析工具箱，根据 operation 路由到对应的 arcpy 矢量分析工具。

    Args:
        operation: 矢量分析类型，可选值 buffer/intersect/union/near/spatial_join/dissolve。
        **kwargs: 各 operation 对应的参数，详见模块级 docstring。

    Returns:
        通过 make_success/make_error 包装的结构化返回值；成功时 result 包含
        output（输出路径）、operation、params 三项。
    """
    arcpy.env.overwriteOutput = True

    # 缓冲区分析
    if operation == "buffer":
        in_features = kwargs["input_features"]
        out_feature_class = kwargs["output_features"]
        buffer_distance_or_field = kwargs["distance"]
        arcpy.analysis.Buffer_analysis(
            in_features,
            out_feature_class,
            buffer_distance_or_field,
            line_side=kwargs.get("line_side", "FULL"),
            line_end_type=kwargs.get("line_end_type", "ROUND"),
            dissolve_option=kwargs.get("dissolve_option", "NONE"),
            dissolve_field=kwargs.get("dissolve_field", None),
            method=kwargs.get("method", "PLANAR"),
        )
        return make_success({"output": out_feature_class, "operation": operation, "params": kwargs})

    # 相交分析
    elif operation == "intersect":
        in_features = kwargs["input_features"]
        out_feature_class = kwargs["output_features"]
        arcpy.analysis.Intersect(
            in_features,
            out_feature_class,
            join_attributes=kwargs.get("join_attributes", "ALL"),
            cluster_tolerance=kwargs.get("cluster_tolerance", ""),
            output_type=kwargs.get("output_type", "INPUT"),
        )
        return make_success({"output": out_feature_class, "operation": operation, "params": kwargs})

    # 联合分析
    elif operation == "union":
        in_features = kwargs["input_features"]
        out_feature_class = kwargs["output_features"]
        arcpy.analysis.Union(
            in_features,
            out_feature_class,
            join_attributes=kwargs.get("join_attributes", "ALL"),
            cluster_tolerance=kwargs.get("cluster_tolerance", ""),
            gaps=kwargs.get("gaps", "GAPS"),
        )
        return make_success({"output": out_feature_class, "operation": operation, "params": kwargs})

    # 近邻分析（近邻信息写入输入要素属性表，输出即输入）
    elif operation == "near":
        in_features = kwargs["input_features"]
        near_features = kwargs["near_features"]
        arcpy.analysis.Near(
            in_features,
            near_features,
            search_radius=kwargs.get("search_radius", None),
            location=kwargs.get("location", "NO_LOCATION"),
            angle=kwargs.get("angle", "NO_ANGLE"),
            method=kwargs.get("method", "PLANAR"),
        )
        return make_success({"output": in_features, "operation": operation, "params": kwargs})

    # 空间连接
    elif operation == "spatial_join":
        target_features = kwargs["target_features"]
        join_features = kwargs["join_features"]
        out_feature_class = kwargs["output_features"]
        arcpy.analysis.SpatialJoin(
            target_features,
            join_features,
            out_feature_class,
            join_operation=kwargs.get("join_operation", "JOIN_ONE_TO_ONE"),
            join_type=kwargs.get("join_type", "KEEP_ALL"),
            field_mapping=kwargs.get("field_mapping", None),
            match_option=kwargs.get("match_option", "INTERSECT"),
            search_radius=kwargs.get("search_radius", None),
            distance_field_name=kwargs.get("distance_field_name", ""),
        )
        return make_success({"output": out_feature_class, "operation": operation, "params": kwargs})

    # 融合
    elif operation == "dissolve":
        in_features = kwargs["input_features"]
        out_feature_class = kwargs["output_features"]
        arcpy.management.Dissolve(
            in_features,
            out_feature_class,
            dissolve_field=kwargs.get("dissolve_fields", None),
            statistics_fields=kwargs.get("statistics_fields", None),
            multi_part=kwargs.get("multi_part", "MULTI_PART"),
            unsplit_lines=kwargs.get("unsplit_lines", "DISSOLVE_LINES"),
        )
        return make_success({"output": out_feature_class, "operation": operation, "params": kwargs})

    # 未支持的 operation
    else:
        return make_error(
            "ValueError",
            f"不支持的 operation: {operation}，支持的 operation: buffer/intersect/union/near/spatial_join/dissolve",
        )
