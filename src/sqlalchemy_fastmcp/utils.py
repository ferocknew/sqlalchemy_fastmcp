"""
公共工具模块
"""

import os
import re
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_database_config() -> Dict[str, str]:
    """
    从环境变量获取数据库配置

    Returns:
        Dict[str, str]: 数据库配置信息
    """
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '3306'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASS', ''),
        'database': os.getenv('DB_NAME', ''),
        'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
        'db_type': os.getenv('DB_TYPE', 'mysql').lower()
    }
    return config

def create_connection_string(config: Dict[str, str]) -> str:
    """根据配置创建数据库连接字符串"""
    if config['db_type'] == 'mysql':
        if config['database']:
            return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"
        else:
            return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}?charset={config['charset']}"
    elif config['db_type'] == 'sqlite':
        # SQLite 使用文件路径作为数据库
        # 如果 database 字段包含路径，直接使用；否则使用默认路径
        db_path = config.get('database', 'database.db')
        if not db_path:
            db_path = 'database.db'
        return f"sqlite:///{db_path}"
    else:
        raise ValueError(f"不支持的数据库类型: {config['db_type']}")

def get_permission_config() -> Dict[str, bool]:
    """从环境变量获取权限配置"""
    def str_to_bool(value: str) -> bool:
        """将字符串转换为布尔值"""
        if isinstance(value, bool):
            return value
        return value.lower() in ('true', '1', 'yes', 'on')

    config = {
        'allow_insert': str_to_bool(os.getenv('ALLOW_INSERT_OPERATION', 'false')),
        'allow_update': str_to_bool(os.getenv('ALLOW_UPDATE_OPERATION', 'false')),
        'allow_delete': str_to_bool(os.getenv('ALLOW_DELETE_OPERATION', 'false'))
    }
    return config

def is_sql_operation_allowed(sql_query: str) -> Tuple[bool, str]:
    """
    检查SQL操作是否被允许

    Args:
        sql_query: SQL查询语句

    Returns:
        Tuple[bool, str]: (是否允许, 错误信息)
    """
    # 获取权限配置
    permissions = get_permission_config()

    # 清理和标准化SQL语句
    sql_clean = re.sub(r'\s+', ' ', sql_query.strip()).upper()

    # 检查INSERT操作
    if not permissions['allow_insert']:
        insert_patterns = [
            r'\bINSERT\s+INTO\b',
            r'\bREPLACE\s+INTO\b',
            r'\bLOAD\s+DATA\b'
        ]
        for pattern in insert_patterns:
            if re.search(pattern, sql_clean):
                return False, "INSERT操作被禁用。当前配置不允许插入数据。"

    # 检查UPDATE操作
    if not permissions['allow_update']:
        update_patterns = [
            r'\bUPDATE\b.*\bSET\b',
            r'\bALTER\s+TABLE\b',
            r'\bALTER\s+DATABASE\b',
            r'\bCREATE\s+TABLE\b',
            r'\bCREATE\s+DATABASE\b',
            r'\bCREATE\s+INDEX\b',
            r'\bDROP\s+INDEX\b',
            r'\bRENAME\s+TABLE\b',
            r'\bTRUNCATE\s+TABLE\b'
        ]
        for pattern in update_patterns:
            if re.search(pattern, sql_clean):
                return False, "UPDATE/ALTER操作被禁用。当前配置不允许修改数据或结构。"

    # 检查DELETE操作
    if not permissions['allow_delete']:
        delete_patterns = [
            r'\bDELETE\s+FROM\b',
            r'\bDROP\s+TABLE\b',
            r'\bDROP\s+DATABASE\b',
            r'\bDROP\s+VIEW\b',
            r'\bDROP\s+PROCEDURE\b',
            r'\bDROP\s+FUNCTION\b'
        ]
        for pattern in delete_patterns:
            if re.search(pattern, sql_clean):
                return False, "DELETE/DROP操作被禁用。当前配置不允许删除数据或结构。"

    return True, ""

def get_version() -> str:
    """
    获取版本号

    优先从_version模块读取（打包后），其次从VERSION文件读取（开发时）

    Returns:
        str: 版本号字符串
    """
    try:
        # 首先尝试从_version模块读取（打包后的环境）
        from ._version import __version__
        return __version__
    except ImportError:
        pass

    try:
        # 开发环境：从VERSION文件读取
        current_dir = os.path.dirname(os.path.abspath(__file__))  # src/sqlalchemy_fastmcp
        src_dir = os.path.dirname(current_dir)  # src
        root_dir = os.path.dirname(src_dir)  # project root
        version_file = os.path.join(root_dir, 'VERSION')

        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                return version
    except Exception:
        pass

    # 如果都失败了，返回默认版本
    return "0.1.0"