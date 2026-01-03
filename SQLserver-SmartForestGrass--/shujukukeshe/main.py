#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧林草系统 - 主程序入口

本程序是智慧林草系统的主入口，负责整合所有业务线模块，提供统一的系统访问接口。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_forest_grass_business import DisasterWarningTerminal


def main():
    """
    主程序入口
    """
    print("=" * 60)
    print("      智慧林草灾害预警系统")
    print("=" * 60)
    print("\n系统正在初始化...")
    
    try:
        # 初始化SQL Server数据库连接
        terminal = DisasterWarningTerminal(db_config={'server': '.\\SQLEXPRESS', 'database': 'SmartForestGrass'})
        terminal.run()
    except Exception as e:
        print(f"\n系统运行出错: {e}")
        print("请检查配置和数据库连接后重试！")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
