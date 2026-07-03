"""地图排版与出图工具箱 Skill 执行函数。

通过 operation 参数选择具体的地图排版与出图操作，统一路由到对应的 arcpy.mp 功能。
支持的 operation：
  - list_maps：列出工程中所有地图
  - list_layouts：列出工程中所有布局
  - create_map：创建新地图
  - create_layout：创建新布局
  - add_layer：向指定地图添加图层
  - remove_layer：从指定地图移除图层
  - set_layer_visibility：设置图层可见性
  - set_map_extent：设置布局中地图框的范围
  - zoom_to_layer：缩放地图框到指定图层全图
  - update_title：修改布局中标题文本
  - update_legend：更新图例显示的图层
  - export_layout：导出布局为图片或 PDF
"""
import arcpy

from core.errors import arcpy_error_handler, make_success, make_error


@arcpy_error_handler
def map_layout(operation, **kwargs):
    """地图排版与出图工具箱，根据 operation 路由到对应的 arcpy.mp 功能。

    Args:
        operation: 排版出图操作类型，可选值 list_maps/list_layouts/create_map/
            create_layout/add_layer/remove_layer/set_layer_visibility/
            set_map_extent/zoom_to_layer/update_title/update_legend/export_layout。
        **kwargs: 各 operation 对应的参数，详见模块级 docstring。

    Returns:
        通过 make_success/make_error 包装的结构化返回值。
    """
    arcpy.env.overwriteOutput = True

    aprx_path = kwargs.get("aprx_path")
    if not aprx_path:
        return make_error("ValueError", "aprx_path 参数为必填")

    # 列出工程中所有地图
    if operation == "list_maps":
        aprx = arcpy.mp.ArcGISProject(aprx_path)
        maps = [m.name for m in aprx.listMaps()]
        return make_success({
            "operation": "list_maps",
            "aprx_path": aprx_path,
            "maps": maps,
        })

    # 列出工程中所有布局
    elif operation == "list_layouts":
        aprx = arcpy.mp.ArcGISProject(aprx_path)
        layouts = [lyt.name for lyt in aprx.listLayouts()]
        return make_success({
            "operation": "list_layouts",
            "aprx_path": aprx_path,
            "layouts": layouts,
        })

    # 创建新地图
    elif operation == "create_map":
        map_name = kwargs["map_name"]

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        new_map = aprx.createMap(map_name)

        aprx.save()
        return make_success({
            "operation": "create_map",
            "aprx_path": aprx_path,
            "map_name": new_map.name,
            "saved": True,
        })

    # 创建新布局
    elif operation == "create_layout":
        layout_name = kwargs["layout_name"]
        page_width = kwargs.get("page_width", 8.5)
        page_height = kwargs.get("page_height", 11)
        page_units = kwargs.get("page_units", "INCHES")

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        new_layout = aprx.createLayout(
            layout_name,
            page_width,
            page_height,
            page_units,
        )

        aprx.save()
        return make_success({
            "operation": "create_layout",
            "aprx_path": aprx_path,
            "layout_name": new_layout.name,
            "page_width": page_width,
            "page_height": page_height,
            "page_units": page_units,
            "saved": True,
        })

    # 向指定地图添加图层
    elif operation == "add_layer":
        map_name = kwargs["map_name"]
        layer_path = kwargs["layer_path"]
        add_position = kwargs.get("add_position", "TOP")

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        map_obj = aprx.listMaps(map_name)[0]

        if layer_path.lower().endswith(".lyrx"):
            layer_file = arcpy.mp.LayerFile(layer_path)
            map_obj.addLayer(layer_file, add_position)
        else:
            map_obj.addDataFromPath(layer_path)

        aprx.save()
        return make_success({
            "operation": "add_layer",
            "aprx_path": aprx_path,
            "map_name": map_name,
            "layer_path": layer_path,
            "saved": True,
        })

    # 从指定地图移除图层
    elif operation == "remove_layer":
        map_name = kwargs["map_name"]
        layer_name = kwargs["layer_name"]

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        map_obj = aprx.listMaps(map_name)[0]

        target_layer = None
        for layer in map_obj.listLayers():
            if layer.name == layer_name:
                target_layer = layer
                break

        if target_layer is None:
            return make_error("ValueError", f"地图 {map_name} 中未找到图层 {layer_name}")

        map_obj.removeLayer(target_layer)
        aprx.save()
        return make_success({
            "operation": "remove_layer",
            "aprx_path": aprx_path,
            "map_name": map_name,
            "layer_name": layer_name,
            "saved": True,
        })

    # 设置图层可见性
    elif operation == "set_layer_visibility":
        map_name = kwargs["map_name"]
        layer_name = kwargs["layer_name"]
        visible = kwargs["visible"]

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        map_obj = aprx.listMaps(map_name)[0]

        target_layer = None
        for layer in map_obj.listLayers():
            if layer.name == layer_name:
                target_layer = layer
                break

        if target_layer is None:
            return make_error("ValueError", f"地图 {map_name} 中未找到图层 {layer_name}")

        target_layer.visible = visible
        aprx.save()
        return make_success({
            "operation": "set_layer_visibility",
            "aprx_path": aprx_path,
            "map_name": map_name,
            "layer_name": layer_name,
            "visible": visible,
            "saved": True,
        })

    # 设置布局中地图框的范围
    elif operation == "set_map_extent":
        layout_name = kwargs["layout_name"]
        extent = kwargs["extent"]
        map_frame_name = kwargs.get("map_frame_name")

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        layout = aprx.listLayouts(layout_name)[0]

        if map_frame_name:
            mf = layout.listElements("MAPFRAME_ELEMENT", map_frame_name)[0]
        else:
            mf = layout.listElements("MAPFRAME_ELEMENT")[0]

        extent_parts = list(map(float, extent.split()))
        mf.camera.setExtent(arcpy.Extent(*extent_parts))
        aprx.save()
        return make_success({
            "operation": "set_map_extent",
            "aprx_path": aprx_path,
            "layout_name": layout_name,
            "extent": extent,
            "saved": True,
        })

    # 缩放地图框到指定图层全图
    elif operation == "zoom_to_layer":
        layout_name = kwargs["layout_name"]
        layer_name = kwargs["layer_name"]
        map_frame_name = kwargs.get("map_frame_name")

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        layout = aprx.listLayouts(layout_name)[0]

        if map_frame_name:
            mf = layout.listElements("MAPFRAME_ELEMENT", map_frame_name)[0]
        else:
            mf = layout.listElements("MAPFRAME_ELEMENT")[0]

        layer = mf.map.listLayers(layer_name)[0]
        mf.camera.setExtent(layer.getOutputExtent())
        aprx.save()
        return make_success({
            "operation": "zoom_to_layer",
            "aprx_path": aprx_path,
            "layout_name": layout_name,
            "layer_name": layer_name,
            "saved": True,
        })

    # 修改布局中标题文本
    elif operation == "update_title":
        layout_name = kwargs["layout_name"]
        title_text = kwargs["title_text"]
        title_element_name = kwargs.get("title_element_name")

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        layout = aprx.listLayouts(layout_name)[0]

        if title_element_name:
            elem = layout.listElements("TEXT_ELEMENT", title_element_name)[0]
        else:
            elem = layout.listElements("TEXT_ELEMENT")[0]

        elem.text = title_text
        aprx.save()
        return make_success({
            "operation": "update_title",
            "aprx_path": aprx_path,
            "layout_name": layout_name,
            "title_text": title_text,
            "saved": True,
        })

    # 更新图例显示的图层
    elif operation == "update_legend":
        layout_name = kwargs["layout_name"]
        visible_layers = kwargs["visible_layers"]
        legend_element_name = kwargs.get("legend_element_name")

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        layout = aprx.listLayouts(layout_name)[0]

        if legend_element_name:
            legend = layout.listElements("LEGEND_ELEMENT", legend_element_name)[0]
        else:
            legend = layout.listElements("LEGEND_ELEMENT")[0]

        map_obj = legend.mapFrame.map
        for layer in map_obj.listLayers():
            layer.visible = layer.name in visible_layers

        aprx.save()
        return make_success({
            "operation": "update_legend",
            "aprx_path": aprx_path,
            "layout_name": layout_name,
            "visible_layers": visible_layers,
            "saved": True,
        })

    # 导出布局为图片或 PDF
    elif operation == "export_layout":
        layout_name = kwargs["layout_name"]
        output_path = kwargs["output_path"]
        fmt = kwargs.get("format", "PDF")
        resolution = kwargs.get("resolution", 300)

        aprx = arcpy.mp.ArcGISProject(aprx_path)
        layout = aprx.listLayouts(layout_name)[0]

        if fmt == "PDF":
            layout.exportToPDF(output_path, resolution=resolution)
        elif fmt == "PNG":
            layout.exportToPNG(output_path, resolution=resolution)
        elif fmt == "JPEG":
            layout.exportToJPEG(output_path, resolution=resolution)
        elif fmt == "TIFF":
            layout.exportToTIFF(output_path, resolution=resolution)
        else:
            return make_error("ValueError", f"不支持的导出格式: {fmt}，支持 PDF/PNG/JPEG/TIFF")

        return make_success({
            "operation": "export_layout",
            "aprx_path": aprx_path,
            "layout_name": layout_name,
            "output_path": output_path,
            "format": fmt,
            "resolution": resolution,
        })

    # 未支持的 operation
    else:
        return make_error(
            "ValueError",
            f"不支持的 operation: {operation}，支持的 operation: list_maps/list_layouts/create_map/create_layout/add_layer/remove_layer/set_layer_visibility/set_map_extent/zoom_to_layer/update_title/update_legend/export_layout",
        )
