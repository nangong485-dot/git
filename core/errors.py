"""
统一的返回格式与错误处理工具。
所有 Skill 的 Python 执行函数都应使用这里的构造器包装返回值，
并使用 arcpy_error_handler 装饰器统一捕获 arcpy.ExecuteError。
"""
import functools
import arcpy


def make_success(result, messages=None):
    """构造成功返回结构。

    Args:
        result: 任意结果数据（字典/列表/字符串等）
        messages: GP 工具消息列表（list[str]），可选

    Returns:
        {"success": True, "result": result, "messages": messages or [], "error": None}
    """
    return {
        "success": True,
        "result": result,
        "messages": messages or [],
        "error": None,
    }


def make_error(error_type, message, messages=None):
    """构造失败返回结构。

    Args:
        error_type: 异常类型名字符串，如 "arcpy.ExecuteError"、"ValueError"
        message: 错误详情字符串
        messages: GP 工具消息列表，可选

    Returns:
        {"success": False, "result": None, "messages": messages or [],
         "error": {"type": error_type, "message": message}}
    """
    return {
        "success": False,
        "result": None,
        "messages": messages or [],
        "error": {
            "type": error_type,
            "message": message,
        },
    }


def _collect_gp_messages():
    """收集 arcpy.GetMessages() 返回的所有 GP 工具消息，按行拆分为列表。

    使用 arcpy.GetMessages() 获取当前会话累积的全部 GP 工具消息，
    按换行拆分并过滤掉空白行，返回 list[str]。
    """
    raw = arcpy.GetMessages()
    # 按行拆分并剔除空白行，避免返回值中混入空字符串
    return [line for line in raw.splitlines() if line.strip()]


def arcpy_error_handler(func):
    """装饰器：统一捕获 arcpy.ExecuteError 与通用 Exception。

    - 捕获 arcpy.ExecuteError 时，error_type 设为 "arcpy.ExecuteError"，
      message 包含异常字符串 + arcpy.GetMessages(2)（错误级别消息）。
    - 捕获其他 Exception 时，error_type 设为异常类名，message 为异常字符串。
    - 任何情况下都不应让被装饰函数抛出未捕获异常。
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except arcpy.ExecuteError as e:
            # 先捕获 arcpy.ExecuteError（必须早于通用 Exception 分支）
            gp_messages = _collect_gp_messages()
            # GetMessages(2) 仅返回错误级别（severity=2）的 GP 消息
            error_messages = arcpy.GetMessages(2)
            # 拼接异常字符串与错误级别 GP 消息
            message = f"{e}\n{error_messages}" if error_messages else str(e)
            return make_error("arcpy.ExecuteError", message, gp_messages)
        except Exception as e:
            # 兜底捕获所有其他异常，error_type 取异常类名
            gp_messages = _collect_gp_messages()
            return make_error(type(e).__name__, str(e), gp_messages)

    return wrapper
