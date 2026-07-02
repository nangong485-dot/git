"""栅格分析工具箱 Skill 执行函数。

通过 operation 参数路由到具体的栅格分析工具，包括：
- reclassify：重分类
- raster_calculator：栅格计算器（基于 arcpy.sa 栅格代数）
- slope：坡度
- aspect：坡向
- contour：等值线

所有栅格分析依赖 Spatial Analyst 扩展（arcpy.sa）。
"""
import arcpy

from arcpy.sa import *
from core.errors import arcpy_error_handler, make_success, make_error


@arcpy_error_handler
def raster_analysis(operation, **kwargs):
    """栅格分析工具箱，通过 operation 参数分派到具体栅格分析工具。

    Args:
        operation: 栅格分析类型，支持 reclassify / raster_calculator /
            slope / aspect / contour 五种。
        **kwargs: 各 operation 对应的参数，详见各分支说明。

    Returns:
        通过 make_success / make_error 包装的结果字典：
        - 成功：result = {"output": <输出路径>, "operation": operation,
          "params": kwargs}
        - 失败：error 字段含 type 与 message
    """
    # 函数入口第一行设置 overwriteOutput，允许覆盖已有输出
    arcpy.env.overwriteOutput = True

    if operation == "reclassify":
        # 重分类：依据字段将栅格像元值重新映射到新值区间
        in_raster = kwargs["in_raster"]
        reclass_field = kwargs["reclass_field"]
        remap = kwargs["remap"]
        out_raster = kwargs["out_raster"]
        # missing_values 默认 "NODATA"，未被重映射覆盖的像元设为 NODATA
        arcpy.sa.Reclassify(
            in_raster,
            reclass_field,
            remap,
            out_raster,
            missing_values="NODATA",
        )
        return make_success({
            "output": out_raster,
            "operation": operation,
            "params": kwargs,
        })

    elif operation == "raster_calculator":
        # 栅格计算器：在受控命名空间中用 eval 求值 arcpy 栅格代数表达式
        expression = kwargs["expression"]
        out_raster = kwargs["out_raster"]
        # rasters 为变量名 -> 栅格路径 的字典，将加载为 Raster 对象注入命名空间
        rasters = kwargs.get("rasters", {})
        namespace = {}
        for name, path in rasters.items():
            namespace[name] = arcpy.sa.Raster(path)
        namespace["__builtins__"] = __builtins__
        # 表达式如 '"raster1" * 2 + "raster2"'，或 'r1 * 2 + r2'（r1/r2 在 rasters 中）
        result_raster = eval(expression, namespace)
        result_raster.save(out_raster)
        return make_success({
            "output": out_raster,
            "operation": operation,
            "params": kwargs,
        })

    elif operation == "slope":
        # 坡度：由 DEM 栅格生成坡度栅格
        in_raster = kwargs["in_raster"]
        out_raster = kwargs["out_raster"]
        output_unit = kwargs.get("output_unit", "DEGREE")
        z_factor = kwargs.get("z_factor", 1)
        # 调用 Slope 后显式保存到指定输出路径
        out = arcpy.sa.Slope(in_raster, output_unit, z_factor)
        out.save(out_raster)
        return make_success({
            "output": out_raster,
            "operation": operation,
            "params": kwargs,
        })

    elif operation == "aspect":
        # 坡向：由 DEM 栅格生成坡向栅格（0-360 度，方位角）
        in_raster = kwargs["in_raster"]
        out_raster = kwargs["out_raster"]
        # Aspect 默认采用 PLANAR 方法
        out = arcpy.sa.Aspect(in_raster)
        out.save(out_raster)
        return make_success({
            "output": out_raster,
            "operation": operation,
            "params": kwargs,
        })

    elif operation == "contour":
        # 等值线：由栅格表面生成等值线矢量要素类
        in_raster = kwargs["in_raster"]
        output_features = kwargs["output_features"]
        contour_interval = kwargs["contour_interval"]
        base_contour = kwargs.get("base_contour", 0)
        z_factor = kwargs.get("z_factor", 1)
        # contour_type 默认 "CONTOUR"，生成常规等值线
        arcpy.sa.Contour(
            in_raster,
            output_features,
            contour_interval,
            base_contour,
            z_factor,
            contour_type="CONTOUR",
        )
        return make_success({
            "output": output_features,
            "operation": operation,
            "params": kwargs,
        })

    else:
        # 未支持的 operation，返回 ValueError 类型的错误
        return make_error(
            "ValueError",
            f"不支持的 operation: {operation}，支持的 operation: reclassify/raster_calculator/slope/aspect/contour",
        )
