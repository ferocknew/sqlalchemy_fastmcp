"""
显示数据库表列表功能
"""

import logging
import json
from typing import Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from ..utils import get_database_config, create_connection_string

logger = logging.getLogger(__name__)

def show_tables(database_name: str = None, page: int = 1, page_size: int = 20, table_name: str = None) -> Dict[str, Any]:
    """
    显示数据库内数据表的列表（支持分页）

    连接到指定的数据库，获取数据表列表，支持分页查询。
    支持 MySQL 和 SQLite 数据库，返回表的详细信息。

    Args:
        database_name: 数据库名称，如果为 None 则使用配置中的默认数据库
        page: 页码，默认第 1 页
        page_size: 每页显示数量，默认 20 条
        table_name: 表名筛选（可选），支持模糊匹配

    Returns:
        Dict[str, Any]: 包含表列表的字典对象

    Raises:
        SQLAlchemyError: 当数据库连接失败时
        Exception: 当其他操作失败时

    Example:
        show_tables("my_database", page=1, page_size=20)
        show_tables("my_database", page=2, page_size=10, table_name="user")

    Note:
        需要在 .env 文件中配置数据库连接信息：
        - DB_HOST: 数据库地址
        - DB_PORT: 数据库端口
        - DB_USER: 数据库用户名
        - DB_PASS: 数据库密码
        - DB_TYPE: 数据库类型（mysql）
        - DB_CHARSET: 数据库编码（可选）
    """
    try:
        # 获取数据库配置
        config = get_database_config()
        logger.info(f"数据库配置: {config}")

        # 如果指定了数据库名称，更新配置
        if database_name:
            config['database'] = database_name

        # 参数校验
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20

        # 创建连接字符串
        connection_string = create_connection_string(config)
        logger.info(f"连接字符串: {connection_string}")

        # 创建引擎
        engine = create_engine(connection_string)

        # 连接并执行查询
        with engine.connect() as connection:
            # 获取表列表 - 根据数据库类型使用不同的查询
            if config['db_type'] == 'sqlite':
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"))
            else:
                result = connection.execute(text("SHOW TABLES"))
            all_tables = [row[0] for row in result.fetchall()]

            # 筛选表名（如果指定了 table_name）
            if table_name:
                all_tables = [t for t in all_tables if table_name.lower() in t.lower()]

            # 计算分页信息
            total_tables = len(all_tables)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_tables = all_tables[start_idx:end_idx]

            # 计算总页数
            total_pages = (total_tables + page_size - 1) // page_size

            # 获取每页表的基本信息（表名和注释）
            tables_info = []
            for table_name in paginated_tables:
                try:
                    if config['db_type'] == 'sqlite':
                        # SQLite 获取表注释（从创建语句中提取）
                        result = connection.execute(text(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'"))
                        create_sql = result.fetchone()[0] if result.fetchone() else ""

                        # 从创建语句中提取注释（SQLite 的注释通常在特定位置）
                        comment = ""
                        if "/*" in create_sql and "*/" in create_sql:
                            import re
                            comment_match = re.search(r'/\*\s*(.*?)\s*\*/', create_sql)
                            if comment_match:
                                comment = comment_match.group(1)

                        tables_info.append({
                            "table_name": table_name,
                            "table_comment": comment
                        })
                    else:
                        # MySQL 获取表注释
                        result = connection.execute(text(f"""
                            SELECT TABLE_COMMENT
                            FROM information_schema.TABLES
                            WHERE TABLE_SCHEMA = DATABASE()
                            AND TABLE_NAME = '{table_name}'
                        """))
                        comment = result.fetchone()
                        table_comment = comment[0] if comment and comment[0] else ""

                        tables_info.append({
                            "table_name": table_name,
                            "table_comment": table_comment
                        })

                except Exception as e:
                    logger.warning(f"获取表 {table_name} 注释失败: {e}")
                    tables_info.append({
                        "table_name": table_name,
                        "table_comment": "",
                        "error": str(e)
                    })

            result_data = {
                "message": f"第 {page} / {total_pages} 页，共 {total_tables} 个表",
                "database": config.get('database', 'default'),
                "total_tables": total_tables,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "tables": tables_info,
                "table_name_filter": table_name
            }

            return result_data

    except SQLAlchemyError as e:
        logger.error(f"数据库连接错误: {e}")
        error_result = {
            "message": f"数据库连接失败: {str(e)}",
            "error": True,
            "error_type": "SQLAlchemyError"
        }
        return error_result
    except Exception as e:
        logger.error(f"未知错误: {e}")
        error_result = {
            "message": f"操作失败: {str(e)}",
            "error": True,
            "error_type": "Exception"
        }
        return error_result
