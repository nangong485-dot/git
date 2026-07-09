# ArcGIS Pro Skill 3.5.2 更新 - 产品需求文档

## Overview
- **Summary**: 将 ArcGIS Pro 自动化 Skill 更新至支持 ArcGIS Pro 3.5.2 版本，更新版本声明并添加新版本特有的工具功能。
- **Purpose**: 确保 Skill 与用户已安装的 ArcGIS Pro 3.5.2 版本兼容，并利用新版本的新功能增强自动化能力。
- **Target Users**: 使用 ArcGIS Pro 3.5.2 的 GIS 分析师、制图师和开发者。

## Goals
- 更新 Skill 文档中的版本声明，从 3.0+ 升级至 3.5.2
- 添加 ArcGIS Pro 3.5 新增的 Parquet 文件支持工具（CreateParquetCache）
- 确保现有工具与 ArcGIS Pro 3.5.2 完全兼容
- 更新安装指南以反映新版本要求

## Non-Goals (Out of Scope)
- 重写现有工具的核心逻辑（除非存在兼容性问题）
- 添加 arcpy.sharing 模块的全部 133 个新属性支持（作为后续迭代）
- 添加 Portal 项目功能支持（作为后续迭代）

## Background & Context
- 当前 Skill 声明兼容 ArcGIS Pro 3.0+
- 用户已将 ArcGIS Pro 更新至 3.5.2 版本
- ArcGIS Pro 3.5 引入了重要的新功能：Parquet 文件支持、CreateParquetCache ArcPy 函数等
- Skill 文件位于 `/workspace/dist/arcgis-pro-skill/` 目录

## Functional Requirements
- **FR-1**: 更新 SKILL.md 中的版本声明为 3.5.2
- **FR-2**: 更新 INSTALL.md 中的版本信息为 3.5.2
- **FR-3**: 在 data_management 工具中添加 CreateParquetCache 操作支持
- **FR-4**: 更新 data_management.json schema 以包含新操作

## Non-Functional Requirements
- **NFR-1**: 更新后的 Skill 必须与 ArcGIS Pro 3.5.2 完全兼容
- **NFR-2**: 所有现有工具的 API 保持向后兼容
- **NFR-3**: 代码风格与现有代码保持一致

## Constraints
- **Technical**: 必须使用 ArcGIS Pro 3.5.2 的 arcpy API
- **Dependencies**: 依赖 ArcGIS Pro 3.5.2 的 Python 环境 (arcgispro-py3)

## Assumptions
- 用户已正确安装 ArcGIS Pro 3.5.2
- 用户已配置好 arcgispro-py3 Python 环境

## Acceptance Criteria

### AC-1: 版本声明更新
- **Given**: SKILL.md 和 INSTALL.md 中当前版本声明为 3.0+
- **When**: 更新版本声明
- **Then**: 文档中版本声明显示为 3.5.2
- **Verification**: `human-judgment`

### AC-2: CreateParquetCache 工具添加
- **Given**: data_management.py 中没有 CreateParquetCache 操作
- **When**: 添加 CreateParquetCache 操作支持
- **Then**: 用户可以调用 data_management(operation="create_parquet_cache", ...) 创建 Parquet 缓存
- **Verification**: `programmatic`

### AC-3: Schema 更新
- **Given**: data_management.json 中没有 create_parquet_cache 操作定义
- **When**: 更新 JSON Schema
- **Then**: Schema 包含 create_parquet_cache 操作的参数定义
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要添加其他 ArcGIS Pro 3.5 新功能的支持？
- [ ] 是否需要更新其他文档（如 FRAMEWORK_README.md）？
