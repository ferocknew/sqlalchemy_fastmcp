#!/usr/bin/env python3
"""
简单的测试脚本来验证 show_databases 功能
"""

import os
import sys
from dotenv import load_dotenv

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 加载 test/.env 文件
load_dotenv('test/.env')

from sqlalchemy_fastmcp.server import get_database_config, create_connection_string
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def show_databases_test():
    """测试 show_databases 功能"""
    try:
        # 获取数据库配置
        config = get_database_config()
        print(f"数据库配置: {config}")
        
        # 创建连接字符串（不指定具体数据库）
        connection_string = create_connection_string(config)
        print(f"连接字符串: {connection_string}")
        
        # 创建引擎
        engine = create_engine(connection_string)
        
        # 连接并执行 SHOW DATABASES 查询
        with engine.connect() as connection:
            result = connection.execute(text("SHOW DATABASES"))
            databases = [row[0] for row in result.fetchall()]
            
            # 过滤掉系统数据库（可选）
            system_dbs = {'information_schema', 'mysql', 'performance_schema', 'sys'}
            user_databases = [db for db in databases if db not in system_dbs]
            
            return {
                "message": "成功获取数据库列表",
                "total_count": len(databases),
                "user_databases": user_databases,
                "all_databases": databases,
                "system_databases": list(system_dbs.intersection(set(databases)))
            }
            
    except SQLAlchemyError as e:
        print(f"数据库连接错误: {e}")
        return {
            "message": f"数据库连接失败: {str(e)}",
            "error": True,
            "error_type": "SQLAlchemyError"
        }
    except Exception as e:
        print(f"未知错误: {e}")
        return {
            "message": f"操作失败: {str(e)}",
            "error": True,
            "error_type": "Exception"
        }

def test_show_databases():
    """测试 show_databases 功能"""
    print("=" * 50)
    print("测试 show_databases 功能")
    print("=" * 50)
    
    # 显示当前配置
    config = get_database_config()
    print(f"数据库配置: {config}")
    
    # 测试 show_databases
    print("\n执行 show_databases...")
    result = show_databases_test()
    
    print(f"结果: {result}")
    
    if 'error' in result and result['error']:
        print(f"❌ 错误: {result['message']}")
    else:
        print(f"✅ 成功: {result['message']}")
        print(f"总数据库数量: {result['total_count']}")
        print(f"用户数据库: {result['user_databases']}")
        print(f"系统数据库: {result['system_databases']}")

if __name__ == "__main__":
    test_show_databases() 