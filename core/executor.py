"""通用 ArcPy 脚本执行器（底层兜底工具）。

提供 `execute_arcpy_code` 函数，作为 ArcGIS Pro Skill 框架的底层兜底方案，
用于在 arcgispro-py3 环境中以受控方式执行任意完整的 Python/ArcPy 脚本。

设计原则：
- 仅当目标 GIS 操作没有对应的原子化专属 Skill 时才使用本执行器；
- 接收的 code 应为完整可执行的 Python 脚本（需自行 import arcpy）；
- 脚本可通过设置 `_result` 变量向调用方返回结构化结果；
- 执行前会强制设置 `arcpy.env.overwriteOutput = True`。
"""
import io
import contextlib
import arcpy

from core.errors import arcpy_error_handler, make_success, make_error, _collect_gp_messages


@arcpy_error_handler
def execute_arcpy_code(code, local_vars=None):
    """通用 ArcPy 脚本执行器（底层兜底）。

    本函数是底层兜底工具，仅当目标 GIS 操作没有对应的原子化专属 Skill 时才使用。
    接收一段完整的 Python 脚本字符串，在受控命名空间中执行，并返回执行结果。

    Args:
        code: 字符串，要执行的 Python 脚本（可含 `import arcpy` 与任意 ArcPy 调用）。
            应为完整可执行的脚本。脚本可通过设置 `_result` 变量向调用方返回结构化结果。
        local_vars: 可选 dict，注入到执行命名空间的预定义变量
            （如 ``{"input_fc": "C:/data/roads.shp"}``）。默认为 None 表示空命名空间。

    Note:
        - 执行前会强制设置 ``arcpy.env.overwriteOutput = True``（spec 强制要求）。
        - 脚本在独立的 globals/locals 命名空间中执行，避免污染本模块全局变量。
        - 外层 ``@arcpy_error_handler`` 装饰器会捕获未处理的 ``arcpy.ExecuteError``
          与 ``Exception``；函数内部对 ``exec`` 显式捕获是为了把错误信息丰富化并
          结构化返回（含 stdout、GP 消息等上下文）。

    Returns:
        dict: 统一返回结构。成功时形如::

            {
                "success": True,
                "result": {
                    "stdout": "<脚本 print 输出>",
                    "return_value": None,  # 若脚本设置 locals_dict["_result"] 则返回它
                    "locals": {"k": "v", ...}  # 序列化后的局部变量（剔除 __ 开头键）
                },
                "messages": [...],  # GP 工具消息列表
                "error": None
            }

            失败时形如::

            {
                "success": False,
                "result": None,
                "messages": [...],
                "error": {"type": "<异常类名>", "message": "<错误详情>"}
            }
    """
    # 强制设置覆盖输出，避免脚本因输出已存在而失败（spec 强制要求）
    arcpy.env.overwriteOutput = True

    # 准备执行命名空间：globals 预置模块名与内建符号，locals 为注入变量的副本
    globals_dict = {
        "__name__": "__execute_arcpy_code__",
        "__builtins__": __builtins__,
    }
    # 复制 local_vars 避免外部 dict 被脚本修改；None 时使用空 dict
    locals_dict = dict(local_vars) if local_vars else {}

    # 用 StringIO 收集脚本中的 print 输出
    stdout_buffer = io.StringIO()

    try:
        # 重定向 stdout 捕获 print 输出，并执行脚本
        with contextlib.redirect_stdout(stdout_buffer):
            exec(code, globals_dict, locals_dict)
    except arcpy.ExecuteError as e:
        # 捕获 ArcPy GP 工具执行错误，拼接异常字符串与错误级别 GP 消息
        gp_messages = _collect_gp_messages()
        error_messages = arcpy.GetMessages(2)
        message = f"{e}\n{error_messages}" if error_messages else str(e)
        return make_error("arcpy.ExecuteError", message, gp_messages)
    except Exception as e:
        # 捕获脚本内部其他语法/运行时错误，结构化返回
        gp_messages = _collect_gp_messages()
        return make_error(type(e).__name__, f"脚本执行失败: {e}", gp_messages)

    # 执行成功：收集 stdout 内容与 GP 消息
    stdout_str = stdout_buffer.getvalue()
    gp_messages = _collect_gp_messages()

    # 序列化返回的局部变量，剔除以 __ 开头的内建键，避免不可序列化对象导致整体失败
    serialized_locals = {
        k: str(v) for k, v in locals_dict.items() if not k.startswith("__")
    }

    # 构造结果结构
    result = {
        "stdout": stdout_str,
        # 预留：若脚本设置 locals_dict["_result"] 则返回它
        "return_value": None,
        "locals": serialized_locals,
    }

    # 若脚本显式设置了 _result 变量，则作为 return_value 回传给调用方
    if "_result" in locals_dict:
        result["return_value"] = locals_dict["_result"]

    return make_success(result, gp_messages)
