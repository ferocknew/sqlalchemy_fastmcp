# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

`sqlalchemy_fastmcp` 是一个基于 FastMCP 框架的模型上下文协议（MCP）服务器，用于操作 MySQL 数据库。项目使用 Python 3.11+ 开发，提供了一系列数据库操作工具，支持查询、连接测试、权限控制等功能。

## 常用开发命令

### 环境设置
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -r requirements.txt
```

### 运行服务器
```bash
# 开发模式运行（stdio）
uvx --from sqlalchemy_fastmcp==1.0.4 sqlalchemy-mcp-server stdio

# 或使用本地代码
python -m sqlalchemy_fastmcp stdio

# 运行特定版本
uvx --index-url https://nexus3.m.6do.me:4000/repository/pypi-group/simple --from sqlalchemy_fastmcp==1.0.4 sqlalchemy-mcp-server stdio
```

### 测试
```bash
# 运行所有测试
python -m unittest discover test/

# 运行特定测试
python -m unittest test.test_show_databases
python -m unittest test.test_simple
```

### 构建和发布
```bash
# 自动构建并发布到 Nexus3
bash ./build_and_publish_uv.sh

# 手动构建
uv run python -m build
```

## 代码架构

### 目录结构
- `src/sqlalchemy_fastmcp/` - 源代码目录
  - `server.py` - 主服务器，定义所有 MCP 工具函数
  - `__main__.py` - CLI 入口，使用 typer 框架
  - `utils.py` - 公共工具函数，包含配置管理
  - `exec_query.py` - SQL 查询执行模块
  - `show_databases.py` - 显示数据库列表
  - `show_tables.py` - 显示数据表列表
  - `get_database_info.py` - 获取数据库配置信息
  - `test_database_connection.py` - 数据库连接测试
  - `set_database_source.py` - 动态设置数据源
- `test/` - 测试目录，使用 unittest 框架
- `.env` - 环境变量配置文件（数据库连接信息）

### 核心架构模式

1. **模块化设计**: 每个数据库操作功能独立成一个模块文件
2. **FastMCP 框架**: 使用装饰器 `@mcp.tool()` 定义 MCP 工具
3. **配置管理**: 通过 `.env` 文件和环境变量管理数据库连接
4. **权限控制**: 支持细粒度的 SQL 操作权限控制
5. **日志系统**: 使用 Python logging 模块，输出到文件避免 stdio 污染

### 重要配置

#### 数据库连接配置
必须在 `.env` 文件中配置：
- `DB_HOST` - 数据库地址
- `DB_PORT` - 数据库端口（默认 3306）
- `DB_USER` - 数据库用户名
- `DB_PASS` - 数据库密码
- `DB_TYPE` - 数据库类型（当前只支持 mysql）
- `DB_CHARSET` - 数据库编码（默认 utf8mb4）

#### 权限控制配置（可选）
- `ALLOW_INSERT_OPERATION` - 允许 INSERT 操作（默认 false）
- `ALLOW_UPDATE_OPERATION` - 允许 UPDATE/ALTER 操作（默认 false）
- `ALLOW_DELETE_OPERATION` - 允许 DELETE/DROP 操作（默认 false）

### MCP 工具函数

服务器提供以下工具函数：
- `show_databases_tool()` - 显示数据库列表
- `get_database_info_tool()` - 获取数据库配置信息
- `test_database_connection_tool()` - 测试数据库连接
- `show_tables_tool(database_name)` - 显示数据表列表
- `exec_query_tool(sql_query, database_name, limit)` - 执行 SQL 查询
- `set_database_source_tool(...)` - 动态设置数据源
- `reset_database_source_tool()` - 重置数据源
- `get_current_database_source_tool()` - 获取当前数据源配置

### 开发注意事项

1. **日志输出**: 在 stdio 模式下，所有用户可见的输出必须使用 `sys.stderr`，避免污染 MCP 协议通信
2. **权限控制**: 默认禁用所有修改操作，需要通过环境变量显式开启
3. **错误处理**: 所有工具函数都有完整的异常处理和日志记录
4. **SQL 安全**: 使用正则表达式检测危险 SQL 操作
5. **连接管理**: 使用 SQLAlchemy 进行数据库连接和操作

### 版本管理

- 版本号存储在 `VERSION` 文件中
- 使用 `update_version.py` 脚本更新版本
- `utils.py` 中的 `get_version()` 函数负责读取版本号

### 测试策略

- 使用 Python unittest 框架
- 测试文件命名格式：`test_<功能名>.py`
- 包含数据库连接测试和功能测试
- 测试文件位置：`test/office_files/模版/` 下包含测试用的 docx 文件