"""数据与工程管理工具箱 Skill 执行函数。

通过 operation 参数路由到具体的数据与工程管理操作，统一调用 arcpy.management
与 arcpy.Describe 完成地理数据库（GDB）、要素类、栅格数据集与表的增删改查。

支持的 operation（共 11 种）：
  - create_gdb：创建文件地理数据库
  - compact_gdb：压缩地理数据库
  - list_feature_classes：列出工作空间中的要素类
  - list_rasters：列出工作空间中的栅格数据集
  - list_tables：列出工作空间中的表
  - create_feature_class：创建要素类（可选空间参考与字段）
  - copy_data：复制数据
  - delete_data：删除数据
  - rename_data：重命名数据
  - describe_data：描述数据集元信息（要素类/栅格/表）
  - create_parquet_cache：为 Parquet 文件创建缓存（ArcGIS Pro 3.5+）

所有分支成功后返回 make_success({"operation": ..., ...})；未支持的 operation
返回 make_error("ValueError", ...)。
"""
import os
import arcpy

from core.errors import arcpy_error_handler, make_success, make_error


@arcpy_error_handler
def data_management(operation, **kwargs):
    """数据与工程管理工具箱，根据 operation 路由到对应的 arcpy 数据管理工具。

    Args:
        operation: 数据管理操作类型，可选值 create_gdb/compact_gdb/
            list_feature_classes/list_rasters/list_tables/create_feature_class/
            copy_data/delete_data/rename_data/describe_data/create_parquet_cache。
        **kwargs: 各 operation 对应的参数，详见模块级 docstring 与各分支注释。

    Returns:
        通过 make_success/make_error 包装的结构化返回值；成功时 result 至少包含
        operation 字段以及 operation 特定的输出信息。
    """
    # 函数入口第一行设置 overwriteOutput，允许覆盖已有输出
    arcpy.env.overwriteOutput = True

    # 创建文件地理数据库
    if operation == "create_gdb":
        out_folder_path = kwargs["out_folder_path"]
        gdb_name = kwargs["gdb_name"]
        arcpy.management.CreateFileGDB(out_folder_path, gdb_name)
        return make_success({
            "operation": "create_gdb",
            "out_folder_path": out_folder_path,
            "gdb_name": gdb_name,
            "output": os.path.join(out_folder_path, gdb_name + ".gdb"),
        })

    # 压缩地理数据库
    elif operation == "compact_gdb":
        gdb_path = kwargs["gdb_path"]
        arcpy.management.Compact(gdb_path)
        return make_success({
            "operation": "compact_gdb",
            "gdb_path": gdb_path,
            "compactted": True,
        })

    # 列出工作空间中的要素类
    elif operation == "list_feature_classes":
        workspace = kwargs["workspace"]
        feature_type = kwargs.get("feature_type")
        # 备份原工作空间，操作完成后恢复
        original_workspace = arcpy.env.workspace
        arcpy.env.workspace = workspace
        try:
            if feature_type:
                feature_classes = arcpy.ListFeatureClasses(feature_type=feature_type)
            else:
                feature_classes = arcpy.ListFeatureClasses()
        finally:
            # 无论是否异常都恢复原工作空间
            arcpy.env.workspace = original_workspace
        return make_success({
            "operation": "list_feature_classes",
            "workspace": workspace,
            "feature_classes": feature_classes,
        })

    # 列出工作空间中的栅格数据集
    elif operation == "list_rasters":
        workspace = kwargs["workspace"]
        # 备份原工作空间，操作完成后恢复
        original_workspace = arcpy.env.workspace
        arcpy.env.workspace = workspace
        try:
            rasters = arcpy.ListRasters()
        finally:
            # 无论是否异常都恢复原工作空间
            arcpy.env.workspace = original_workspace
        return make_success({
            "operation": "list_rasters",
            "workspace": workspace,
            "rasters": rasters,
        })

    # 列出工作空间中的表
    elif operation == "list_tables":
        workspace = kwargs["workspace"]
        # 备份原工作空间，操作完成后恢复
        original_workspace = arcpy.env.workspace
        arcpy.env.workspace = workspace
        try:
            tables = arcpy.ListTables()
        finally:
            # 无论是否异常都恢复原工作空间
            arcpy.env.workspace = original_workspace
        return make_success({
            "operation": "list_tables",
            "workspace": workspace,
            "tables": tables,
        })

    # 创建要素类（可选空间参考与字段）
    elif operation == "create_feature_class":
        out_path = kwargs["out_path"]
        out_name = kwargs["out_name"]
        geometry_type = kwargs["geometry_type"]
        spatial_reference = kwargs.get("spatial_reference")

        # 处理空间参考：WKID 整数或坐标系名称/路径字符串均通过 SpatialReference 构造
        sr = None
        if spatial_reference is not None:
            if isinstance(spatial_reference, int):
                sr = arcpy.SpatialReference(spatial_reference)
            else:
                # 字符串名称或 .prj 路径也支持
                sr = arcpy.SpatialReference(spatial_reference)

        # 创建要素类
        out_fc = arcpy.management.CreateFeatureclass(
            out_path, out_name, geometry_type, spatial_reference=sr
        )

        # 添加字段：每项为 [字段名, 字段类型]
        fields = kwargs.get("fields", [])
        for field_name, field_type in fields:
            arcpy.management.AddField(out_fc, field_name, field_type)

        return make_success({
            "operation": "create_feature_class",
            "out_path": out_path,
            "out_name": out_name,
            "geometry_type": geometry_type,
            "output": os.path.join(out_path, out_name),
            "fields_added": len(fields),
        })

    # 复制数据
    elif operation == "copy_data":
        in_data = kwargs["in_data"]
        out_data = kwargs["out_data"]
        data_type = kwargs.get("data_type")
        if data_type:
            arcpy.management.Copy(in_data, out_data, data_type)
        else:
            arcpy.management.Copy(in_data, out_data)
        return make_success({
            "operation": "copy_data",
            "in_data": in_data,
            "out_data": out_data,
            "output": out_data,
        })

    # 删除数据
    elif operation == "delete_data":
        in_data = kwargs["in_data"]
        data_type = kwargs.get("data_type")
        if data_type:
            arcpy.management.Delete(in_data, data_type)
        else:
            arcpy.management.Delete(in_data)
        return make_success({
            "operation": "delete_data",
            "in_data": in_data,
            "deleted": True,
        })

    # 重命名数据
    elif operation == "rename_data":
        in_data = kwargs["in_data"]
        out_data = kwargs["out_data"]
        data_type = kwargs.get("data_type")
        if data_type:
            arcpy.management.Rename(in_data, out_data, data_type)
        else:
            arcpy.management.Rename(in_data, out_data)
        return make_success({
            "operation": "rename_data",
            "in_data": in_data,
            "out_data": out_data,
            "output": out_data,
        })

    # 描述数据集元信息（要素类/栅格/表）
    elif operation == "describe_data":
        in_data = kwargs["in_data"]
        desc = arcpy.Describe(in_data)
        result_info = {
            "name": desc.name,
            "path": desc.catalogPath,
            "data_type": desc.dataType,
            "dataset_type": getattr(desc, "datasetType", None),
        }

        # 空间参考（如有）
        if hasattr(desc, "spatialReference"):
            sr = desc.spatialReference
            result_info["spatial_reference"] = {
                "name": sr.name if sr else None,
                "wkid": sr.factoryCode if sr else None,
                "type": sr.type if sr else None,
            }

        # 要素类：几何类型、字段
        if desc.dataType in ("FeatureClass", "ShapeFile"):
            result_info["geometry_type"] = desc.shapeType
            result_info["fields"] = [
                {"name": f.name, "type": f.type, "length": getattr(f, "length", None)}
                for f in desc.fields
            ]

        # 栅格：波段数
        if desc.dataType in ("RasterDataset", "RasterBand"):
            result_info["band_count"] = getattr(desc, "bandCount", None)
            result_info["format"] = getattr(desc, "format", None)

        # 表：字段
        if desc.dataType in ("Table",):
            result_info["fields"] = [
                {"name": f.name, "type": f.type} for f in desc.fields
            ]

        return make_success({
            "operation": "describe_data",
            "in_data": in_data,
            "description": result_info,
        })

    # 为 Parquet 文件创建缓存（ArcGIS Pro 3.5+）
    elif operation == "create_parquet_cache":
        input_path = kwargs["input_path"]
        output_cache_path = kwargs["output_cache_path"]
        arcpy.da.CreateParquetCache(input_path, output_cache_path)
        return make_success({
            "operation": "create_parquet_cache",
            "input_path": input_path,
            "output_cache_path": output_cache_path,
            "output": output_cache_path,
        })

    # 未支持的 operation
    else:
        return make_error(
            "ValueError",
            f"不支持的 operation: {operation}，支持的 operation: create_gdb/compact_gdb/list_feature_classes/list_rasters/list_tables/create_feature_class/copy_data/delete_data/rename_data/describe_data/create_parquet_cache",
        )
