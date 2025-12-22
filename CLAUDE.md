# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

`sqlalchemy_fastmcp` 是一个基于 FastMCP 框架的模型上下文协议（MCP）服务器，用于操作 MySQL 和 SQLite 数据库。项目使用 Python 3.11+ 开发，提供了一系列数据库操作工具，支持查询、连接测试、权限控制、SSH隧道等功能。

## 常用开发命令

### 环境设置
-  python 版本 3.12
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
uvx --from sqlalchemy_fastmcp==1.2.6 sqlalchemy-mcp-server stdio

# 或使用本地代码
python -m sqlalchemy_fastmcp stdio
```

### 测试
由于缺少 `test` 目录，无法提供具体的测试命令。如果项目包含测试，请补充相关命令。

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
  - `utils.py` - 公共工具函数，包含配置管理和权限控制
  - `tools/` - 各个 MCP 工具的具体实现模块
- `pyproject.toml` - 项目配置文件，包含依赖和打包设置
- `VERSION` - 存储项目版本号的文件
- `.env` - 环境变量配置文件（用于数据库连接信息）

### 核心架构模式

1. **模块化设计**: 每个数据库操作功能被拆分为独立的模块，放在 `src/sqlalchemy_fastmcp/tools/` 目录下。
2. **FastMCP 框架**: 使用 `@mcp.tool()` 装饰器在 `server.py` 中将功能模块注册为 MCP 工具。
3. **配置管理**: 通过 `.env` 文件和环境变量加载数据库连接信息，`utils.py` 中的 `get_database_config` 负责读取。
4. **权限控制**: 在 `utils.py` 中通过 `is_sql_operation_allowed` 函数实现对 SQL 操作的权限检查，默认禁用写操作。
5. **动态版本**: 版本号存储在根目录的 `VERSION` 文件中，并通过 `pyproject.toml` 的 `tool.setuptools.dynamic` 配置动态加载。

### 重要配置

#### 数据库连接配置
必须在 `.env` 文件或环境变量中配置：
- `DB_TYPE` - 数据库类型 (`mysql` 或 `sqlite`)
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_NAME` - MySQL 连接参数
- `DB_NAME` - SQLite 数据库文件路径

#### 权限控制配置（可选）
- `ALLOW_INSERT_OPERATION` - 是否允许 INSERT 操作（默认 `false`）
- `ALLOW_UPDATE_OPERATION` - 是否允许 UPDATE/ALTER 操作（默认 `false`）
- `ALLOW_DELETE_OPERATION` - 是否允许 DELETE/DROP 操作（默认 `false`）

### MCP 工具函数
服务器在 `server.py` 中定义了以下工具，具体实现在 `tools/` 目录下：
- `show_databases_tool()`
- `get_database_info_tool()`
- `test_database_connection_tool()`
- `show_tables_tool()`
- `exec_query_tool()`
- `set_database_source_tool()`
- `reset_database_source_tool()`
- `get_current_database_source_tool()`
- `set_database_source_on_ssh_tool()`
- `stop_ssh_tunnel_tool()`
- `get_ssh_tunnel_status_tool()`

### 开发注意事项

1. **日志输出**: 在 stdio 模式下，所有用户可见的输出必须使用 `sys.stderr`，避免污染 MCP 协议通信。
2. **SQL 安全**: `exec_query_tool` 中的权限检查使用正则表达式来防止不允许的 SQL 操作。
3. **版本管理**: 版本号由 `update_version.py` 脚本管理，并写入 `VERSION` 文件。
