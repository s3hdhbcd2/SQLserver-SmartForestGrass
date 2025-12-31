from modules.base_module import BaseModule
import datetime
import json
import os

class StatisticalAnalysisModule(BaseModule):
    """
    统计分析业务线模块
    """
    def __init__(self, db_connection):
        """
        初始化统计分析模块
        :param db_connection: 数据库连接对象
        """
        super().__init__(db_connection)
    
    def create_tables(self):
        """
        创建统计分析相关表
        :return: 是否创建成功
        """
        sql_files = [
            'sql_files/basic_tables.sql',
            'sql_files/environmental_monitoring.sql',
            'sql_files/resource_management.sql',
            'sql_files/equipment_management.sql',
            'sql_files/statistical_analysis.sql'
        ]
        
        for sql_file in sql_files:
            if not self.execute_sql_file(sql_file):
                return False
        return True
    
    def add_report_template(self, template_name, report_type, statistical_indicators, description=None):
        """
        添加报表模板
        :param template_name: 模板名称
        :param report_type: 报表类型
        :param statistical_indicators: 统计指标（JSON格式）
        :param description: 模板描述（可选）
        :return: 模板ID
        """
        try:
            template_id = self.generate_id("TEMP")
            
            # SQL Server版本
            sql = """
            INSERT INTO ReportTemplate (TemplateID, ReportName, ReportType, StatisticalIndicators, Description, CreateTime)
            VALUES (?, ?, ?, ?, ?, GETDATE())
            """
            params = (template_id, template_name, report_type, statistical_indicators, description)
            
            if self.db.execute(sql, params):
                return template_id
            return None
        except Exception as e:
            print(f"添加报表模板失败: {e}")
            return None
    
    def get_report_templates(self, report_type=None):
        """
        获取报表模板列表
        :param report_type: 报表类型（可选）
        :return: 报表模板列表
        """
        try:
            conditions = []
            params = []
            
            if report_type:
                conditions.append("ReportType = ?")
                params.append(report_type)
            
            if conditions:
                sql = f"SELECT * FROM ReportTemplate WHERE {' AND '.join(conditions)}"
            else:
                sql = "SELECT * FROM ReportTemplate"
            
            results = self.db.fetch_all(sql, params)
            templates = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                templates.append({
                    'TemplateID': result[0],
                    'ReportName': result[1],
                    'ReportType': result[2],
                    'StatisticalIndicators': result[3],
                    'Description': result[4],
                    'CreateTime': result[5]
                })
            return templates
        except Exception as e:
            print(f"获取报表模板列表失败: {e}")
            return []
    
    def get_report_template(self, template_id):
        """
        获取单个报表模板
        :param template_id: 模板ID
        :return: 报表模板信息或None
        """
        try:
            sql = "SELECT * FROM ReportTemplate WHERE TemplateID = ?"
            result = self.db.fetch_one(sql, (template_id,))
            
            if result:
                # 使用索引访问，兼容SQL Server
                return {
                    'template_id': result[0],
                    'template_name': result[1],
                    'report_type': result[2],
                    'statistical_indicators': result[3],
                    'description': result[4],
                    'create_time': result[5]
                }
            return None
        except Exception as e:
            print(f"获取报表模板失败: {e}")
            return None
    
    def generate_report_from_template(self, template_id, region_id, start_time, end_time, generated_by):
        """
        基于模板生成报表
        :param template_id: 模板ID
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param generated_by: 生成人员ID
        :return: 生成的报表ID
        """
        try:
            # 获取模板信息
            template = self.get_report_template(template_id)
            if not template:
                print(f"报表模板不存在: {template_id}")
                return None
            
            # 解析统计指标
            statistical_indicators = json.loads(template['StatisticalIndicators'])
            
            # 根据报表类型生成不同的报表内容
            report_content = ""
            if template['ReportType'] == '环境监测':
                # 生成环境监测报表
                report_content = self.generate_monitoring_report(region_id, start_time, end_time)
            elif template['ReportType'] == '设备状态':
                # 生成设备状态报表
                report_content = self.generate_device_status_report(region_id, start_time, end_time)
            elif template['ReportType'] == '资源统计':
                # 生成资源统计报表
                report_content = self.generate_resource_statistics_report(region_id, start_time, end_time)
            
            # 生成报表文件名
            report_id = self.generate_id("REP")
            report_name = f"{template['TemplateName']}_{region_id}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}"
            
            # 确保报表目录存在
            os.makedirs('reports', exist_ok=True)
            report_path = f"reports/{report_id}.txt"
            
            # 保存报表内容到文件
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # 保存报表信息到数据库 - SQL Server版本
            sql = """
            INSERT INTO generated_report (report_id, report_name, template_id, region_id, start_time, end_time, report_content, report_file_path, generated_time, generated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
            """
            params = (report_id, report_name, template_id, region_id, start_time, end_time, report_content, report_path, generated_by)
            
            if self.db.execute(sql, params):
                return report_id
            return None
        except Exception as e:
            print(f"生成报表失败: {e}")
            return None
    
    def generate_monitoring_report(self, region_id, start_time, end_time):
        """
        生成环境监测报表
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 报表内容
        """
        try:
            # 获取监测数据
            sql = """
            SELECT * FROM monitoring_data 
            WHERE region_id = ? AND data_time BETWEEN ? AND ? 
            ORDER BY data_time DESC
            """
            params = (region_id, start_time, end_time)
            results = self.db.fetch_all(sql, params)
            
            if not results:
                return "该时间段内没有监测数据。"
            
            # 生成报表
            report = f"环境监测报表\n"
            report += f"区域ID: {region_id}\n"
            report += f"时间范围: {start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}\n"
            report += f"数据数量: {len(results)}\n"
            report += "=" * 80 + "\n"
            report += f"{'时间':<20} {'温度':<8} {'湿度':<8} {'风速':<8} {'降雨量':<8} {'病虫害':<8} {'烟雾':<8} {'土壤湿度':<8}\n"
            report += "=" * 80 + "\n"
            
            for result in results[:50]:  # 只显示前50条
                # 使用索引访问，兼容SQL Server
                data_time = result[3]
                temperature = result[4]
                humidity = result[5]
                wind_speed = result[6]
                rainfall = result[7]
                pest_disease = result[8]
                smoke = result[9]
                soil_moisture = result[10]
                
                report += f"{data_time.strftime('%Y-%m-%d %H:%M'):<20} {temperature:<8.1f} {humidity:<8.1f} {wind_speed:<8.1f} {rainfall:<8.1f} {pest_disease:<8} {smoke:<8} {soil_moisture:<8.1f}\n"
            
            if len(results) > 50:
                report += f"... 共 {len(results)} 条数据，仅显示前50条\n"
            
            return report
        except Exception as e:
            print(f"生成环境监测报表失败: {e}")
            return f"生成报表失败: {str(e)}"
    
    def generate_device_status_report(self, region_id, start_time, end_time):
        """
        生成设备状态报表
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 报表内容
        """
        try:
            # 获取设备档案
            device_sql = "SELECT * FROM device_archive WHERE region_id = ?"
            devices = self.db.fetch_all(device_sql, (region_id,))
            
            report = f"设备状态报表\n"
            report += f"区域ID: {region_id}\n"
            report += f"时间范围: {start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}\n"
            report += f"设备数量: {len(devices)}\n"
            report += "=" * 80 + "\n"
            
            for device in devices:
                # 使用索引访问，兼容SQL Server
                device_id = device[0]
                device_name = device[1]
                device_type = device[2]
                
                report += f"设备: {device_name}（{device_id}）- {device_type}\n"
                report += "-" * 80 + "\n"
                
                # 获取设备状态
                status_sql = """
                SELECT * FROM device_status 
                WHERE device_id = ? AND collection_time BETWEEN ? AND ? 
                ORDER BY collection_time DESC
                """
                status_results = self.db.fetch_all(status_sql, (device_id, start_time, end_time))
                
                if status_results:
                    report += f"{'时间':<20} {'运行状态':<15} {'电池电量':<10} {'信号强度':<10}\n"
                    report += "-" * 80 + "\n"
                    
                    for status in status_results[:10]:  # 每个设备只显示最近10条状态
                        # 使用索引访问，兼容SQL Server
                        col_time = status[2]
                        running_status = status[3]
                        battery = status[4]
                        signal = status[5]
                        
                        report += f"{col_time.strftime('%Y-%m-%d %H:%M'):<20} {running_status:<15} {battery:<10.1f}% {signal:<10}\n"
                    
                    if len(status_results) > 10:
                        report += f"... 共 {len(status_results)} 条状态记录，仅显示最近10条\n"
                else:
                    report += "该时间段内没有设备状态记录\n"
                
                report += "\n"
            
            return report
        except Exception as e:
            print(f"生成设备状态报表失败: {e}")
            return f"生成报表失败: {str(e)}"
    
    def generate_resource_statistics_report(self, region_id, start_time, end_time):
        """
        生成资源统计报表
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 报表内容
        """
        try:
            # 获取林草资源
            resource_sql = "SELECT * FROM forest_resource WHERE region_id = ?"
            resources = self.db.fetch_all(resource_sql, (region_id,))
            
            # 获取资源变动记录
            change_sql = """
            SELECT * FROM resource_change_record 
            WHERE resource_id IN (SELECT resource_id FROM forest_resource WHERE region_id = ?) 
            AND change_time BETWEEN ? AND ?
            ORDER BY change_time DESC
            """
            changes = self.db.fetch_all(change_sql, (region_id, start_time, end_time))
            
            report = f"资源统计报表\n"
            report += f"区域ID: {region_id}\n"
            report += f"时间范围: {start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}\n"
            report += "=" * 80 + "\n"
            
            # 资源概况
            report += "【资源概况】\n"
            if resources:
                total_area = sum(r[3] for r in resources)  # 使用索引访问，兼容SQL Server
                resource_types = set(r[2] for r in resources)  # 使用索引访问，兼容SQL Server
                
                report += f"总资源数量: {len(resources)}\n"
                report += f"总面积: {total_area:.2f} 平方公里\n"
                report += f"资源类型: {', '.join(resource_types)}\n"
            else:
                report += "该区域没有林草资源记录\n"
            
            report += "\n【资源变动记录】\n"
            if changes:
                report += f"{'时间':<20} {'资源ID':<12} {'变动类型':<15} {'变动原因':<30}\n"
                report += "-" * 80 + "\n"
                
                for change in changes:
                    # 使用索引访问，兼容SQL Server
                    change_time = change[4]
                    resource_id = change[1]
                    change_type = change[2]
                    change_reason = change[3]
                    
                    report += f"{change_time.strftime('%Y-%m-%d %H:%M'):<20} {resource_id:<12} {change_type:<15} {change_reason[:28]:<30}\n"
            else:
                report += "该时间段内没有资源变动记录\n"
            
            return report
        except Exception as e:
            print(f"生成资源统计报表失败: {e}")
            return f"生成报表失败: {str(e)}"
    
    def get_generated_reports(self, region_id=None, report_type=None, start_time=None, end_time=None):
        """
        获取生成的报表列表
        :param region_id: 区域ID（可选）
        :param report_type: 报表类型（可选）
        :param start_time: 开始时间（可选）
        :param end_time: 结束时间（可选）
        :return: 生成的报表列表
        """
        try:
            conditions = []
            params = []
            
            if region_id:
                conditions.append("gr.region_id = ?")
                params.append(region_id)
            if report_type:
                conditions.append("rt.report_type = ?")
                params.append(report_type)
            if start_time:
                conditions.append("gr.generated_time >= ?")
                params.append(start_time)
            if end_time:
                conditions.append("gr.generated_time <= ?")
                params.append(end_time)
            
            if conditions:
                sql = f"""
                SELECT gr.*, rt.ReportName, rt.ReportType 
                FROM GeneratedReport gr
                JOIN ReportTemplate rt ON gr.TemplateID = rt.TemplateID
                WHERE {' AND '.join(conditions)} 
                ORDER BY gr.GeneratedTime DESC
                """
            else:
                sql = """
                SELECT gr.*, rt.ReportName, rt.ReportType 
                FROM GeneratedReport gr
                JOIN ReportTemplate rt ON gr.TemplateID = rt.TemplateID
                ORDER BY gr.GeneratedTime DESC
                """
            
            results = self.db.fetch_all(sql, params)
            generated_reports = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                generated_reports.append({
                    'report_id': result[0],
                    'report_name': result[1],
                    'template_id': result[2],
                    'template_name': result[11],
                    'report_type': result[12],
                    'region_id': result[3],
                    'start_time': result[4],
                    'end_time': result[5],
                    'report_content': result[6],
                    'report_file_path': result[7],
                    'generated_time': result[8],
                    'generated_by': result[9]
                })
            return generated_reports
        except Exception as e:
            print(f"获取生成的报表列表失败: {e}")
            return []
