#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行区域表列名更新脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_forest_grass_business import DatabaseConnection

def execute_update_script():
    """
    执行区域表列名更新脚本
    """
    print("=" * 60)
    print("          执行区域表列名更新脚本")
    print("=" * 60)
    
    try:
        # 创建数据库连接
        db_conn = DatabaseConnection()
        if not db_conn.connect():
            print("❌ 数据库连接失败")
            return False
        
        print("✅ 数据库连接成功")
        
        # 读取SQL更新脚本内容
        update_script_path = "sql_files/update_region_column_names.sql"
        with open(update_script_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"✅ 已读取SQL更新脚本，共 {len(sql_content)} 个字符")
        
        # 执行SQL脚本（按GO分隔执行）
        sql_commands = sql_content.split('GO')
        success_count = 0
        error_count = 0
        
        for cmd in sql_commands:
            cmd = cmd.strip()
            if not cmd:
                continue
            
            try:
                # 使用cursor属性执行SQL命令
                db_conn.cursor.execute(cmd)
                # 如果是修改表结构的命令，需要提交事务
                if any(keyword in cmd.upper() for keyword in ['ALTER', 'RENAME', 'CREATE', 'DROP', 'EXEC']):
                    db_conn.connection.commit()
                success_count += 1
            except Exception as e:
                print(f"❌ 执行SQL命令失败: {e}")
                print(f"   失败的命令: {cmd[:100]}...")
                error_count += 1
        
        print(f"\n✅ SQL脚本执行完成: {success_count} 个命令执行成功，{error_count} 个命令执行失败")
        
        # 关闭数据库连接
        if db_conn.cursor:
            db_conn.cursor.close()
        if db_conn.connection:
            db_conn.connection.close()
        print("✅ 数据库连接已关闭")
        
        print("\n" + "=" * 60)
        print("          区域表列名更新完成")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = execute_update_script()
    sys.exit(0 if success else 1)
