"""
显示数据库列表功能
"""

import logging
import json
from typing import Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from ..utils import get_database_config, create_connection_string

logger = logging.getLogger(__name__)

def show_databases() -> Dict[str, Any]:
    """
    显示数据库列表

    连接到配置的数据库服务器，获取所有可用的数据库列表。
    支持 MySQL 数据库，自动过滤系统数据库。

    Returns:
        Dict[str, Any]: 包含数据库列表的字典对象

    Raises:
        SQLAlchemyError: 当数据库连接失败时
        Exception: 当其他操作失败时

    Example:
        show_databases()

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

        # SQLite 不支持多数据库，返回当前数据库信息
        if config['db_type'] == 'sqlite':
            db_path = config.get('database', 'database.db')
            result_data = {
                "message": "SQLite 使用单文件数据库，不支持列出多个数据库",
                "db_type": "sqlite",
                "current_database": db_path,
                "total_count": 1,
                "user_databases": [db_path],
                "all_databases": [db_path],
                "system_databases": []
            }
            return result_data

        # 创建连接字符串（不指定具体数据库）
        connection_string = create_connection_string(config)
        logger.info(f"连接字符串: {connection_string}")

        # 创建引擎
        engine = create_engine(connection_string)

        # 连接并执行 SHOW DATABASES 查询
        with engine.connect() as connection:
            result = connection.execute(text("SHOW DATABASES"))
            databases = [row[0] for row in result.fetchall()]

            # 过滤掉系统数据库（可选）
            system_dbs = {'information_schema', 'mysql', 'performance_schema', 'sys'}
            user_databases = [db for db in databases if db not in system_dbs]

            result_data = {
                "message": "成功获取数据库列表",
                "total_count": len(databases),
                "user_databases": user_databases,
                "all_databases": databases,
                "system_databases": list(system_dbs.intersection(set(databases)))
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
