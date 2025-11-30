"""
测试 show_databases 功能
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy_fastmcp.server import get_database_config, create_connection_string
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def show_databases_test():
    """测试版本的 show_databases 功能"""
    try:
        # 获取数据库配置
        config = get_database_config()

        # 创建连接字符串（不指定具体数据库）
        connection_string = create_connection_string(config)

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
        return {
            "message": f"数据库连接失败: {str(e)}",
            "error": True,
            "error_type": "SQLAlchemyError"
        }
    except Exception as e:
        return {
            "message": f"操作失败: {str(e)}",
            "error": True,
            "error_type": "Exception"
        }

class TestShowDatabases(unittest.TestCase):

    def setUp(self):
        """测试前的设置"""
        # 加载测试环境变量
        load_dotenv('../.env', override=True)

    def test_get_database_config(self):
        """测试数据库配置获取"""
        config = get_database_config()

        self.assertIsInstance(config, dict)
        self.assertIn('host', config)
        self.assertIn('port', config)
        self.assertIn('user', config)
        self.assertIn('password', config)
        self.assertIn('database', config)
        self.assertIn('charset', config)
        self.assertIn('db_type', config)

    def test_create_connection_string(self):
        """测试连接字符串创建"""
        config = {
            'host': 'localhost',
            'port': '3306',
            'user': 'root',
            'password': 'test',
            'database': 'testdb',
            'charset': 'utf8mb4',
            'db_type': 'mysql'
        }

        connection_string = create_connection_string(config)
        self.assertIn('mysql+pymysql://', connection_string)
        self.assertIn('localhost:3306', connection_string)
        self.assertIn('root:test', connection_string)

    @patch('sqlalchemy_fastmcp.server.create_engine')
    @patch('sqlalchemy_fastmcp.server.get_database_config')
    def test_show_databases_success(self, mock_get_config, mock_create_engine):
        """测试成功获取数据库列表"""
        # 模拟配置
        mock_get_config.return_value = {
            'host': 'localhost',
            'port': '3306',
            'user': 'root',
            'password': 'test',
            'database': '',
            'charset': 'utf8mb4',
            'db_type': 'mysql'
        }

        # 模拟数据库连接和查询结果
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ('testdb1',),
            ('testdb2',),
            ('information_schema',),
            ('mysql',)
        ]
        mock_connection.execute.return_value = mock_result

        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        # 执行测试
        result = show_databases_test()

        # 验证结果
        self.assertIn('message', result)
        self.assertIn('total_count', result)
        self.assertIn('user_databases', result)
        self.assertIn('all_databases', result)
        self.assertEqual(result['total_count'], 4)
        self.assertEqual(len(result['user_databases']), 2)
        self.assertIn('testdb1', result['user_databases'])
        self.assertIn('testdb2', result['user_databases'])

    @patch('sqlalchemy_fastmcp.server.create_engine')
    @patch('sqlalchemy_fastmcp.server.get_database_config')
    def test_show_databases_connection_error(self, mock_get_config, mock_create_engine):
        """测试数据库连接错误"""
        # 模拟配置
        mock_get_config.return_value = {
            'host': 'invalid_host',
            'port': '3306',
            'user': 'root',
            'password': 'test',
            'database': '',
            'charset': 'utf8mb4',
            'db_type': 'mysql'
        }

        # 模拟连接错误
        mock_create_engine.side_effect = SQLAlchemyError("Connection failed")

        # 执行测试
        result = show_databases_test()

        # 验证结果
        self.assertIn('error', result)
        self.assertTrue(result['error'])
        self.assertIn('SQLAlchemyError', result['error_type'])

class TestShowDatabasesIntegration(unittest.TestCase):
    """集成测试 - 实际连接数据库"""

    def setUp(self):
        """测试前的设置"""
        # 加载测试环境变量
        load_dotenv('../.env', override=True)

    def test_show_databases_integration(self):
        """集成测试：实际连接数据库并获取数据库列表"""
        try:
            # 获取数据库配置
            config = get_database_config()
            print(f"测试配置: {config}")

            # 创建连接字符串
            connection_string = create_connection_string(config)
            print(f"连接字符串: {connection_string}")

            # 执行 show_databases
            result = show_databases_test()

            # 验证结果
            self.assertIn('message', result)
            if 'error' in result and result['error']:
                print(f"❌ 连接失败: {result['message']}")
                # 连接失败时跳过测试
                self.skipTest(f"数据库连接失败: {result['message']}")
            else:
                print(f"✅ 连接成功: {result['message']}")
                self.assertIn('total_count', result)
                self.assertIn('user_databases', result)
                self.assertIn('all_databases', result)
                self.assertIsInstance(result['total_count'], int)
                self.assertIsInstance(result['user_databases'], list)
                self.assertIsInstance(result['all_databases'], list)

                print(f"总数据库数量: {result['total_count']}")
                print(f"用户数据库: {result['user_databases']}")
                print(f"系统数据库: {result['system_databases']}")

        except Exception as e:
            print(f"测试异常: {e}")
            self.fail(f"集成测试失败: {e}")

if __name__ == '__main__':
    unittest.main()