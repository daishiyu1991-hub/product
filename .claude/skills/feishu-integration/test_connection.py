#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书连通性测试脚本
=================
独立运行，测试所有飞书配置项是否正常。

用法:
  python test_connection.py
"""

import os
import sys

# 将当前目录加入 path 以导入 feishu_sdk
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feishu_sdk import test_connection

if __name__ == "__main__":
    results = test_connection()
    # 退出码：全部通过=0，部分失败=1，全未配置=2
    configured = [v for v in results.values() if v is not None]
    if not configured:
        sys.exit(2)
    elif all(v for v in configured):
        sys.exit(0)
    else:
        sys.exit(1)
