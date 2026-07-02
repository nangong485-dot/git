"""通用 ArcPy 脚本执行器（底层兜底工具）。

提供 `execute_arcpy_code` 函数，作为 ArcGIS Pro Skill 框架的底层兜底方案，
用于在 arcgispro-py3 环境中以受控方式执行任意完整的 Python/ArcPy 脚本，
并通过标准输出（stdout/stderr）捕获脚本执行结果。

设计原则：
- 仅当目标 GIS 操作没有对应的原子化专属 Skill 时才使用本执行器；
- 接收的 code 应为完整可执行的 Python 脚本（需自行 import arcpy）；
- 执行结果以字符串形式返回，包含 stdout 与 stderr 的所有输出；
- 脚本内部应自行使用 try...except 捕获 arcpy.ExecuteError 并通过 print 输出错误信息；
- 执行器本身也会捕获系统级异常，确保不崩溃，并返回完整 traceback。
"""
import sys
import io
import traceback
import arcpy


def execute_arcpy_code(code):
    """在本地 ArcGIS Pro 环境中执行 Python/ArcPy 脚本并返回结果。

    接收大模型传来的 Python 代码字符串，在本地 arcgispro-py3 环境执行，
    捕获 stdout 和 stderr 并以字符串形式返回。若代码执行失败，返回完整的
    错误堆栈与已输出的日志。

    Args:
        code: 字符串，需要执行的完整 Python 脚本代码。
            代码必须遵循以下 Coding Rules：
            1. 基础设置：始终在代码开头包含 import arcpy。
            2. 环境覆盖：始终包含 arcpy.env.overwriteOutput = True。
            3. 输出打印：通过 print() 语句输出关键的执行节点和最终结果路径。
            4. 错误处理：使用 try...except 块，专门捕获 arcpy.ExecuteError。
            5. 路径规范：使用原始字符串（如 r"C:\\data\\map.aprx"）或正斜杠。
            6. 独立运行：每次传入的代码必须是自包含的完整脚本。

    Returns:
        str: 脚本执行的输出结果。
            - 成功时：返回脚本 print 的所有输出（stdout + stderr 合并）；
              若脚本没有任何输出，返回 "代码执行成功，但没有打印任何输出。"。
            - 失败时：返回 "执行失败:\\n<traceback>\\n输出日志:\\n<已输出内容>"。

    Note:
        - 运行环境必须是 ArcGIS Pro 的 Python 克隆环境 (arcgispro-py3)。
        - 在生产环境中，直接 exec 存在安全风险，仅限本地受信任的 Agent 使用。
        - 执行器会强制设置 arcpy.env.overwriteOutput = True，脚本无需重复设置。
    """
    # 创建一个 StringIO 对象来捕获 stdout 和 stderr
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    sys.stdout = captured_output
    sys.stderr = captured_output

    try:
        # 执行前强制设置覆盖输出（Coding Rules 第 2 条的兜底保障）
        arcpy.env.overwriteOutput = True

        # 使用 exec 执行大模型传来的代码
        # 注意：在生产环境中，直接 exec 存在安全风险，仅限本地受信任的 Agent 使用
        exec(code, {"__builtins__": __builtins__, "arcpy": arcpy})
        execution_result = captured_output.getvalue()

        if not execution_result.strip():
            return "代码执行成功，但没有打印任何输出。"
        return execution_result

    except Exception:
        # 捕获执行过程中的系统级 Python 崩溃，返回完整 traceback 与已输出日志
        error_traceback = traceback.format_exc()
        return f"执行失败:\n{error_traceback}\n输出日志:\n{captured_output.getvalue()}"

    finally:
        # 恢复标准输出与标准错误，确保即使发生异常也不会污染外部环境
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        captured_output.close()
