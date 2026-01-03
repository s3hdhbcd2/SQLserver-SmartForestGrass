#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧林草灾害预警系统 - 全部功能测试文件

本测试文件用于测试系统的所有主要功能，包括：
1. 环境监测模块
2. 灾害预警模块
3. 资源管理模块
4. 设备管理模块
5. 统计分析模块

使用方法：
python test_all_features.py
"""

import sys
import os
import datetime
import traceback
from smart_forest_grass_business import DatabaseConnection, DisasterWarningDatabase

# 测试结果统计
class TestResult:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
    
    def add_passed(self):
        self.total_tests += 1
        self.passed_tests += 1
    
    def add_failed(self, test_name, error_msg):
        self.total_tests += 1
        self.failed_tests += 1
        self.errors.append((test_name, error_msg))
    
    def print_summary(self):
        print("\n" + "="*80)
        print("                  测试结果汇总")
        print("="*80)
        print(f"总测试用例数: {self.total_tests}")
        print(f"通过测试数: {self.passed_tests}")
        print(f"失败测试数: {self.failed_tests}")
        print(f"测试通过率: {round(self.passed_tests/self.total_tests*100, 2)}%" if self.total_tests > 0 else "无测试用例")
        
        if self.errors:
            print("\n" + "="*80)
            print("                   失败测试详情")
            print("="*80)
            for i, (test_name, error_msg) in enumerate(self.errors, 1):
                print(f"\n{i}. 测试用例: {test_name}")
                print(f"   失败原因: {error_msg}")
        
        print("\n" + "="*80)
        print("测试完成！")
        print("="*80)

# 功能测试类
class SystemFeatureTester:
    def __init__(self):
        self.db_conn = None
        self.db_instance = None
        self.test_result = TestResult()
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_region_id = "R001"
        self.test_user_id = "U001"
    
    def connect_db(self):
        """连接数据库"""
        try:
            self.db_conn = DatabaseConnection()
            if self.db_conn.connect():
                self.db_instance = DisasterWarningDatabase(self.db_conn)
                return True
            return False
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def disconnect_db(self):
        """断开数据库连接"""
        if self.db_conn:
            self.db_conn.disconnect()
    
    def test_environmental_monitoring(self):
        """测试环境监测模块"""
        print("\n" + "="*60)
        print("          测试环境监测模块")
        print("="*60)
        
        # 测试1: 查看传感器列表
        try:
            sensors = self.db_instance.get_sensors()
            if sensors:
                print(f"✅ 测试通过: 查看传感器列表成功，共 {len(sensors)} 个传感器")
                self.test_result.add_passed()
            else:
                print(f"⚠️  测试警告: 传感器列表为空")
                self.test_result.add_passed()
        except Exception as e:
            print(f"❌ 测试失败: 查看传感器列表失败 - {e}")
            self.test_result.add_failed("查看传感器列表", str(e))
        
        # 测试2: 查看区域监测数据
        try:
            # 使用前30天作为查询范围
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(days=30)
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            
            data = self.db_instance.get_monitoring_data_by_area(
                region_id=self.test_region_id,
                start_time=start_time_str,
                end_time=end_time_str
            )
            if data is not None:
                print(f"✅ 测试通过: 查看区域监测数据成功，共 {len(data)} 条记录")
                self.test_result.add_passed()
            else:
                print(f"⚠️  测试警告: 区域监测数据为空")
                self.test_result.add_passed()
        except Exception as e:
            print(f"❌ 测试失败: 查看区域监测数据失败 - {e}")
            self.test_result.add_failed("查看区域监测数据", str(e))
        

    
    def test_disaster_warning(self):
        """测试灾害预警模块"""
        print("\n" + "="*60)
        print("          测试灾害预警模块")
        print("="*60)
        
        # 测试1: 查看预警规则
        try:
            rules = self.db_instance.get_warning_rules()
            if rules:
                print(f"✅ 测试通过: 查看预警规则成功，共 {len(rules)} 条规则")
                self.test_result.add_passed()
            else:
                print(f"⚠️  测试警告: 预警规则列表为空")
                self.test_result.add_passed()
        except Exception as e:
            print(f"❌ 测试失败: 查看预警规则失败 - {e}")
            self.test_result.add_failed("查看预警规则", str(e))
        
        # 测试2: 查看预警记录
        try:
            warnings = self.db_instance.get_warnings_by_area(self.test_region_id)
            if warnings is not None:
                print(f"✅ 测试通过: 查看预警记录成功，共 {len(warnings)} 条记录")
                self.test_result.add_passed()
            else:
                print(f"⚠️  测试警告: 预警记录为空")
                self.test_result.add_passed()
        except Exception as e:
            print(f"❌ 测试失败: 查看预警记录失败 - {e}")
            self.test_result.add_failed("查看预警记录", str(e))
    
    def test_resource_management(self):
        """测试资源管理模块"""
        print("\n" + "="*60)
        print("          测试资源管理模块")
        print("="*60)
        
        # 测试1: 查看林草资源
        try:
            resources = self.db_instance.get_forest_resources()
            if resources:
                print(f"✅ 测试通过: 查看林草资源成功，共 {len(resources)} 条记录")
                self.test_result.add_passed()
            else:
                print(f"⚠️  测试警告: 林草资源列表为空")
                self.test_result.add_passed()
        except Exception as e:
            print(f"❌ 测试失败: 查看林草资源失败 - {e}")
            self.test_result.add_failed("查看林草资源", str(e))
        
        # 测试2: 查看资源变动记录
        try:
            records = self.db_instance.get_resource_change_records()
            if records is not None:
                print(f"✅ 测试通过: 查看资源变动记录成功，共 {len(records)} 条记录")
                self.test_result.add_passed()
            else:
                print(f"⚠️  测试警告: 资源变动记录为空")
                self.test_result.add_passed()
        except Exception as e:
            print(f"❌ 测试失败: 查看资源变动记录失败 - {e}")
            self.test_result.add_failed("查看资源变动记录", str(e))
    
    def test_equipment_management(self):
        """测试设备管理模块"""
        print("\n" + "="*60)
        print("          测试设备管理模块")
        print("="*60)
        
        # 测试1: 查看设备档案
        try:
            devices = self.db_instance.get_device_archives()
            if devices:
                print(f"✅ 测试通过: 查看设备档案成功，共 {len(devices)} 个设备")
                self.test_result.add_passed()
            else:
                print(f"⚠️  测试警告: 设备档案列表为空")
                self.test_result.add_passed()
        except Exception as e:
            print(f"❌ 测试失败: 查看设备档案失败 - {e}")
            self.test_result.add_failed("查看设备档案", str(e))
    
    def test_statistical_analysis(self):
        """测试统计分析模块"""
        print("\n" + "="*60)
        print("          测试统计分析模块")
        print("="*60)
        
        # 测试1: 查看报表模板
        try:
            templates = self.db_instance.get_report_templates()
            if templates:
                print(f"✅ 测试通过: 查看报表模板成功，共 {len(templates)} 个模板")
                self.test_result.add_passed()
            else:
                print(f"⚠️  测试警告: 报表模板列表为空")
                self.test_result.add_passed()
        except Exception as e:
            print(f"❌ 测试失败: 查看报表模板失败 - {e}")
            self.test_result.add_failed("查看报表模板", str(e))
    
    def test_complex_queries(self):
        """测试复杂查询功能"""
        print("\n" + "="*60)
        print("          测试复杂查询功能")
        print("="*60)
        
        # 测试复杂查询功能
        try:
            # 使用测试数据进行查询1: 火灾预警及处理情况
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(days=7)
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            
            result = self.db_instance.complex_queries(1, start_time=start_time_str, end_time=end_time_str)
            if result is not None:
                print(f"✅ 测试通过: 复杂查询1成功，共 {len(result)} 条记录")
                self.test_result.add_passed()
            else:
                print(f"⚠️  测试警告: 复杂查询1结果为空")
                self.test_result.add_passed()
        except Exception as e:
            print(f"❌ 测试失败: 复杂查询1失败 - {e}")
            self.test_result.add_failed("复杂查询1", str(e))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("="*80)
        print("      智慧林草灾害预警系统 - 功能测试")
        print("="*80)
        print(f"测试开始时间: {self.current_time}")
        
        # 连接数据库
        if not self.connect_db():
            print("数据库连接失败，测试无法继续")
            return False
        
        try:
            # 运行各个模块的测试
            self.test_environmental_monitoring()
            self.test_disaster_warning()
            self.test_resource_management()
            self.test_equipment_management()
            self.test_statistical_analysis()
            self.test_complex_queries()
            
            # 打印测试结果
            self.test_result.print_summary()
            
            return self.test_result.failed_tests == 0
        except Exception as e:
            print(f"测试过程中发生错误: {e}")
            traceback.print_exc()
            return False
        finally:
            # 断开数据库连接
            self.disconnect_db()

# 主函数
if __name__ == "__main__":
    tester = SystemFeatureTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
