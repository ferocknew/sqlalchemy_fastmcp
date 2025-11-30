"""
测试 set_database_source 功能
"""

import unittest
import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy_fastmcp.set_database_source import set_database_source, reset_database_source, get_current_database_config

class TestSetDatabaseSource(unittest.TestCase):
    """测试数据库数据源设置功能"""

    def setUp(self):
        """测试前准备"""
        # 重置数据库配置
        reset_database_source()

    def tearDown(self):
        """测试后清理"""
        # 重置数据库配置
        reset_database_source()

    def test_set_database_source_invalid_type(self):
        """测试设置不支持的数据库类型"""
        result = set_database_source(
            db_type="postgresql",
            db_host="localhost",
            db_port=5432,
            db_username="test",
            db_password="test"
        )

        result_data = json.loads(result)
        self.assertFalse(result_data['success'])
        self.assertTrue(result_data['error'])
        self.assertEqual(result_data['error_type'], 'ValueError')
        self.assertIn('不支持的数据库类型', result_data['message'])

    def test_set_database_source_connection_fail(self):
        """测试连接失败的情况"""
        result = set_database_source(
            db_type="mysql",
            db_host="invalid_host",
            db_port=3306,
            db_username="invalid_user",
            db_password="invalid_password"
        )

        result_data = json.loads(result)
        self.assertFalse(result_data['success'])
        self.assertTrue(result_data['error'])
        # 可能是 SQLAlchemyError 或 Exception（如缺少依赖）
        self.assertIn(result_data['error_type'], ['SQLAlchemyError', 'Exception'])
        self.assertIn('失败', result_data['message'])

    def test_set_database_source_parameters(self):
        """测试参数设置"""
        # 测试默认参数
        config = get_current_database_config()

        # 应该使用环境变量配置
        self.assertIsNotNone(config)
        self.assertIn('host', config)
        self.assertIn('port', config)
        self.assertIn('user', config)

    def test_reset_database_source(self):
        """测试重置数据库数据源"""
        result = reset_database_source()

        result_data = json.loads(result)
        self.assertTrue(result_data['success'])
        self.assertIn('已重置为环境变量配置', result_data['message'])
        self.assertIn('config', result_data)

    def test_get_current_database_config(self):
        """测试获取当前数据库配置"""
        config = get_current_database_config()

        # 检查配置包含必要的字段
        required_fields = ['host', 'port', 'user', 'password', 'database', 'charset', 'db_type']
        for field in required_fields:
            self.assertIn(field, config)

    def test_config_parameters_validation(self):
        """测试配置参数验证"""
        # 测试各种参数组合
        test_cases = [
            {
                'db_type': 'mysql',
                'db_host': 'test_host',
                'db_port': 3306,
                'db_username': 'test_user',
                'db_password': 'test_pass',
                'db_database_name': 'test_db',
                'db_charset': 'utf8mb4'
            },
            {
                'db_type': 'mysql',
                'db_host': '192.168.1.100',
                'db_port': 3307,
                'db_username': 'admin',
                'db_password': '',
                'db_database_name': '',
                'db_charset': 'utf8'
            }
        ]

        for case in test_cases:
            with self.subTest(case=case):
                # 由于无法连接到实际数据库，预期会失败
                result = set_database_source(**case)
                result_data = json.loads(result)

                # 应该包含配置信息
                if not result_data['success']:
                    self.assertIn('config', result_data)
                    config = result_data['config']
                    self.assertEqual(config['db_type'], case['db_type'])
                    self.assertEqual(config['host'], case['db_host'])
                    self.assertEqual(config['port'], case['db_port'])
                    self.assertEqual(config['user'], case['db_username'])

def set_database_source_test():
    """简单测试函数，用于快速验证"""
    print("开始测试 set_database_source 功能...")

    # 测试不支持的数据库类型
    print("\n1. 测试不支持的数据库类型:")
    result = set_database_source(db_type="postgresql")
    print(result)

    # 测试连接失败
    print("\n2. 测试连接失败:")
    result = set_database_source(
        db_type="mysql",
        db_host="invalid_host",
        db_username="invalid_user"
    )
    print(result)

    # 测试重置配置
    print("\n3. 测试重置配置:")
    result = reset_database_source()
    print(result)

    # 测试获取当前配置
    print("\n4. 测试获取当前配置:")
    config = get_current_database_config()
    print(json.dumps(config, ensure_ascii=False, indent=2))

    print("\n测试完成!")

if __name__ == '__main__':
    # 运行简单测试
    set_database_source_test()

    print("\n" + "="*50)
    print("运行单元测试:")

    # 运行单元测试
    unittest.main(verbosity=2)
