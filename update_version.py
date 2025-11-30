#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建时更新版本号脚本
从VERSION文件读取版本号并更新_version.py文件
"""

import os

def update_version():
    """更新版本号"""
    # 读取VERSION文件
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    with open(version_file, 'r') as f:
        version = f.read().strip()

    # 更新_version.py文件
    version_py_file = os.path.join(os.path.dirname(__file__), 'src', 'sqlalchemy_fastmcp', '_version.py')
    version_py_content = '# 这个文件在构建时自动生成\n# 请不要手动编辑\n__version__ = "{}"\n'.format(version)

    with open(version_py_file, 'w') as f:
        f.write(version_py_content)

    print("版本号已更新为: {}".format(version))

if __name__ == '__main__':
    update_version()
