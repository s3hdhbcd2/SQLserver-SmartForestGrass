#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行SQL脚本工具
用于执行指定的SQL脚本文件
"""

import pyodbc
import sys


def execute_sql_script(script_path):
    """
    执行指定路径的SQL脚本
    :param script_path: SQL脚本文件路径
    :return: 执行结果
    """
    try:
        # 连接数据库
        conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=.\\SQLEXPRESS;DATABASE=SmartForestGrass;Trusted_Connection=yes"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print(f"成功连接到数据库，正在执行脚本: {script_path}")

        # 读取SQL脚本内容
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 按GO分隔SQL语句块
        sql_blocks = sql_content.split('GO')

        # 执行每个SQL语句块
        for i, block in enumerate(sql_blocks):
            block = block.strip()
            if not block:
                continue

            try:
                print(f"正在执行SQL块 {i+1}/{len(sql_blocks)}...")
                cursor.execute(block)
                conn.commit()
                print(f"SQL块 {i+1} 执行成功")
            except Exception as e:
                print(f"执行SQL块 {i+1} 失败: {e}")
                conn.rollback()
                raise

        print(f"\n脚本 {script_path} 执行完成！")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"执行脚本时发生错误: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python run_sql_script.py <脚本路径>")
        sys.exit(1)

    script_path = sys.argv[1]
    execute_sql_script(script_path)
