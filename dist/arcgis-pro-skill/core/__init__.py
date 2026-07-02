"""ArcGIS Pro Skill 框架基础设施包。

导出统一的返回格式构造器与异常捕获装饰器，供各 Skill 复用。
"""
from .errors import make_success, make_error, arcpy_error_handler

__all__ = ["make_success", "make_error", "arcpy_error_handler"]
