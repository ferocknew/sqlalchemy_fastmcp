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

def show_tables(database_name: str = None) -> Dict[str, Any]:
    """
    显示当前数据库内数据表的列表

    连接到指定的数据库，获取所有数据表的列表。
    支持 MySQL 数据库，返回表的详细信息。

    Args:
        database_name: 数据库名称，如果为 None 则使用配置中的默认数据库

    Returns:
        Dict[str, Any]: 包含表列表的字典对象

    Raises:
        SQLAlchemyError: 当数据库连接失败时
        Exception: 当其他操作失败时

    Example:
        show_tables("my_database")

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
            tables = [row[0] for row in result.fetchall()]

            # 获取每个表的详细信息
            tables_info = []
            for table_name in tables:
                try:
                    if config['db_type'] == 'sqlite':
                        # SQLite 使用 PRAGMA 获取表结构
                        result = connection.execute(text(f"PRAGMA table_info(`{table_name}`)"))
                        columns = []
                        for row in result.fetchall():
                            columns.append({
                                "field": row[1],  # name
                                "type": row[2],   # type
                                "null": "NO" if row[3] == 1 else "YES",  # notnull
                                "key": "PRI" if row[5] == 1 else "",  # pk
                                "default": row[4],  # dflt_value
                                "extra": ""
                            })

                        # 获取表的行数
                        result = connection.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                        row_count = result.fetchone()[0]

                        # 获取表的创建语句
                        result = connection.execute(text(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'"))
                        create_statement = result.fetchone()[0]

                        tables_info.append({
                            "table_name": table_name,
                            "columns": columns,
                            "row_count": row_count,
                            "create_statement": create_statement
                        })
                    else:
                        # MySQL 使用 DESCRIBE
                        result = connection.execute(text(f"DESCRIBE `{table_name}`"))
                        columns = []
                        for row in result.fetchall():
                            columns.append({
                                "field": row[0],
                                "type": row[1],
                                "null": row[2],
                                "key": row[3],
                                "default": row[4],
                                "extra": row[5]
                            })

                        # 获取表的行数
                        result = connection.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                        row_count = result.fetchone()[0]

                        # 获取表的创建信息
                        result = connection.execute(text(f"SHOW CREATE TABLE `{table_name}`"))
                        create_statement = result.fetchone()[1]

                        tables_info.append({
                            "table_name": table_name,
                            "columns": columns,
                            "row_count": row_count,
                            "create_statement": create_statement
                        })

                except Exception as e:
                    logger.warning(f"获取表 {table_name} 信息失败: {e}")
                    tables_info.append({
                        "table_name": table_name,
                        "error": str(e)
                    })

            result_data = {
                "message": "成功获取表列表",
                "database": config.get('database', 'default'),
                "total_tables": len(tables),
                "tables": tables_info
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
