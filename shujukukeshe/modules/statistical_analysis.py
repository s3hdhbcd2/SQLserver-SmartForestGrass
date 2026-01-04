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
    
    def add_report_template(self, template_name, report_type, statistical_indicators, description=None, 
                           statistical_dimension='区域/时间/类型', generation_cycle='月'):
        """
        添加报表模板
        :param template_name: 模板名称
        :param report_type: 报表类型
        :param statistical_indicators: 统计指标（JSON格式）
        :param description: 模板描述（可选）
        :param statistical_dimension: 统计维度（区域/时间/类型）
        :param generation_cycle: 生成周期（日/周/月）
        :return: 模板ID
        """
        try:
            template_id = self.generate_id("TEMP")
            
            # SQL Server版本
            sql = """
            INSERT INTO ReportTemplate (TemplateID, ReportName, ReportType, StatisticalIndicators, Description, CreateTime, 
                                      StatisticalDimension, GenerationCycle, IsActive, AuditStatus)
            VALUES (?, ?, ?, ?, ?, GETDATE(), ?, ?, 1, '待审核')
            """
            params = (template_id, template_name, report_type, statistical_indicators, description, 
                     statistical_dimension, generation_cycle)
            
            if self.db.execute(sql, params):
                return template_id
            return None
        except Exception as e:
            print(f"添加报表模板失败: {e}")
            return None
    
    def get_report_templates(self, report_type=None, audit_status=None, is_active=None):
        """
        获取报表模板列表
        :param report_type: 报表类型（可选）
        :param audit_status: 审核状态（可选）
        :param is_active: 是否启用（可选）
        :return: 报表模板列表
        """
        try:
            # 为每个查询创建一个新的数据库连接，避免连接繁忙问题
            new_conn = self.db.get_new_connection()
            
            # 构建基础SQL查询，只查询表中实际存在的字段
            sql = "SELECT TemplateID, ReportName, ReportType, StatisticalIndicators, Description, CreateTime, "
            sql += "StatisticalDimension, GenerationCycle, IsActive, AuditStatus "
            sql += "FROM ReportTemplate"
            
            conditions = []
            params = []
            
            # 添加查询条件
            if report_type:
                conditions.append("ReportType = ?")
                params.append(report_type)
            
            if audit_status:
                conditions.append("AuditStatus = ?")
                params.append(audit_status)
            
            if is_active is not None:
                conditions.append("IsActive = ?")
                params.append(1 if is_active else 0)
            
            # 应用where子句
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            # 执行查询
            results = new_conn.fetch_all(sql, params)
            
            # 处理结果
            templates = []
            for result in results:
                try:
                    template = {
                        'TemplateID': result[0],
                        'ReportName': result[1],
                        'ReportType': result[2],
                        'statistical_indicators': result[3],
                        'Description': result[4],
                        'CreateTime': result[5],
                        'AuditStatus': result[9] if len(result) > 9 else '未审核',
                        'IsActive': result[8] if len(result) > 8 else 1,
                        'StatisticalDimension': result[6] if len(result) > 6 else '',
                        'GenerationCycle': result[7] if len(result) > 7 else ''
                    }
                    templates.append(template)
                except IndexError as e:
                    print(f"处理模板数据时发生索引错误: {e}")
            
            # 关闭新创建的连接
            new_conn.disconnect()
            
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
                    'create_time': result[5],
                    'statistical_dimension': result[6],
                    'generation_cycle': result[7],
                    'is_active': result[8],
                    'audit_status': result[9],
                    'audit_by': result[10],
                    'audit_time': result[11],
                    'audit_comments': result[12]
                }
            return None
        except Exception as e:
            print(f"获取报表模板失败: {e}")
            return None
    
    def audit_report_template(self, template_id, audit_status, audit_by, audit_comments=None):
        """
        审核报表模板
        :param template_id: 模板ID
        :param audit_status: 审核状态（已通过/已拒绝）
        :param audit_by: 审核人ID
        :param audit_comments: 审核意见（可选）
        :return: 是否审核成功
        """
        try:
            sql = """
            UPDATE ReportTemplate 
            SET AuditStatus = ?, AuditBy = ?, AuditTime = GETDATE(), AuditComments = ?
            WHERE TemplateID = ?
            """
            params = (audit_status, audit_by, audit_comments, template_id)
            
            return self.db.execute(sql, params)
        except Exception as e:
            print(f"审核报表模板失败: {e}")
            return False
    
    def update_report_template_status(self, template_id, is_active):
        """
        更新报表模板状态（启用/禁用）
        :param template_id: 模板ID
        :param is_active: 是否启用
        :return: 是否更新成功
        """
        try:
            sql = "UPDATE ReportTemplate SET IsActive = ? WHERE TemplateID = ?"
            params = (1 if is_active else 0, template_id)
            
            return self.db.execute(sql, params)
        except Exception as e:
            print(f"更新报表模板状态失败: {e}")
            return False
    
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
            statistical_indicators = json.loads(template['statistical_indicators'])
            
            # 根据报表类型生成不同的报表内容
            report_content = ""
            if template['report_type'] == '环境监测':
                # 生成环境监测报表
                report_content = self.generate_monitoring_report(region_id, start_time, end_time)
            elif template['report_type'] == '设备状态':
                # 生成设备状态报表
                report_content = self.generate_device_status_report(region_id, start_time, end_time)
            elif template['report_type'] == '资源统计':
                # 生成资源统计报表
                report_content = self.generate_resource_statistics_report(region_id, start_time, end_time)
            
            # 生成报表文件名，直接生成GR0001格式的ID
            # 简单实现：使用当前时间的毫秒数作为ID的数字部分
            import time
            # 获取当前时间的毫秒数，取最后4位
            current_time = int(time.time() * 1000)
            # 取最后4位作为数字部分
            num_part = current_time % 10000
            # 格式化新ID为GR0001格式
            report_id = f"GR{num_part:04d}"
            report_name = f"{template['template_name']}_{region_id}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}"
            
            # 确保报表目录存在
            os.makedirs('reports', exist_ok=True)
            report_path = f"reports/{report_id}.txt"
            
            # 保存报表内容到文件
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # 生成统计周期（如2024-10）
            statistical_cycle = f"{start_time.year}-{start_time.month:02d}"
            
            # 数据来源说明
            data_source_desc = f"数据来源于区域{region_id}在{start_time}至{end_time}期间的监测数据和资源数据"
            
            # 保存报表信息到数据库 - SQL Server版本
            # 只插入表中实际存在的10列
            sql = """
            INSERT INTO GeneratedReport (ReportID, ReportName, TemplateID, RegionID, StartTime, EndTime, ReportContent, 
                                      ReportFilePath, GeneratedTime, GeneratedBy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
            """
            params = (report_id, report_name, template_id, region_id, start_time, end_time, report_content, 
                     report_path, generated_by)
            
            if self.db.execute(sql, params):
                return report_id
            return None
        except Exception as e:
            print(f"生成报表失败: {e}")
            return None
    
    def generate_monitoring_report(self, region_id, start_time, end_time):
        """
        生成环境监测报表（JSON格式，支持图表可视化）
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 结构化的报表数据
        """
        import json
        try:
            # 获取监测数据
            sql = """
            SELECT * FROM MonitoringData 
            WHERE RegionID = ? AND DataTime BETWEEN ? AND ? 
            ORDER BY DataTime DESC
            """
            params = (region_id, start_time, end_time)
            results = self.db.fetch_all(sql, params)
            
            if not results:
                # 返回结构化的空数据
                return json.dumps({
                    "type": "环境监测",
                    "region_id": region_id,
                    "time_range": f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}",
                    "total_data": 0,
                    "message": "该时间段内没有监测数据。",
                    "chart_data": {
                        "labels": [],
                        "datasets": []
                    },
                    "raw_data": []
                }, ensure_ascii=False)
            
            # 准备图表数据
            time_labels = []
            temperature_data = []
            humidity_data = []
            wind_speed_data = []
            rainfall_data = []
            
            # 转换数据格式
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
                
                time_labels.append(data_time.strftime('%Y-%m-%d %H:%M'))
                temperature_data.append(float(temperature))
                humidity_data.append(float(humidity))
                wind_speed_data.append(float(wind_speed))
                rainfall_data.append(float(rainfall))
            
            # 构建报表数据
            report_data = {
                "type": "环境监测",
                "region_id": region_id,
                "time_range": f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}",
                "total_data": len(results),
                "message": f"共 {len(results)} 条数据，仅显示前50条",
                "chart_data": {
                    "labels": time_labels,
                    "datasets": [
                        {
                            "label": "温度",
                            "data": temperature_data,
                            "borderColor": "rgb(255, 99, 132)",
                            "backgroundColor": "rgba(255, 99, 132, 0.2)",
                            "borderWidth": 2,
                            "tension": 0.1
                        },
                        {
                            "label": "湿度",
                            "data": humidity_data,
                            "borderColor": "rgb(54, 162, 235)",
                            "backgroundColor": "rgba(54, 162, 235, 0.2)",
                            "borderWidth": 2,
                            "tension": 0.1
                        },
                        {
                            "label": "风速",
                            "data": wind_speed_data,
                            "borderColor": "rgb(75, 192, 192)",
                            "backgroundColor": "rgba(75, 192, 192, 0.2)",
                            "borderWidth": 2,
                            "tension": 0.1
                        },
                        {
                            "label": "降雨量",
                            "data": rainfall_data,
                            "borderColor": "rgb(153, 102, 255)",
                            "backgroundColor": "rgba(153, 102, 255, 0.2)",
                            "borderWidth": 2,
                            "tension": 0.1
                        }
                    ]
                },
                "raw_data": results[:50]  # 保留原始数据用于表格显示
            }
            
            # 返回JSON字符串
            return json.dumps(report_data, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"生成环境监测报表失败: {e}")
            return json.dumps({
                "type": "环境监测",
                "region_id": region_id,
                "time_range": f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}",
                "total_data": 0,
                "message": f"生成报表失败: {str(e)}",
                "chart_data": {
                    "labels": [],
                    "datasets": []
                },
                "raw_data": []
            }, ensure_ascii=False)
    
    def generate_device_status_report(self, region_id, start_time, end_time):
        """
        生成设备状态报表（JSON格式，支持图表可视化）
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 结构化的报表数据
        """
        import json
        try:
            # 获取设备列表
            device_sql = "SELECT * FROM DeviceArchive WHERE RegionID = ?"
            devices = self.db.fetch_all(device_sql, (region_id,))
            
            if not devices:
                # 返回结构化的空数据
                return json.dumps({
                    "type": "设备状态",
                    "region_id": region_id,
                    "time_range": f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}",
                    "total_devices": 0,
                    "message": "该区域没有设备。",
                    "chart_data": {
                        "labels": [],
                        "datasets": []
                    },
                    "raw_data": []
                }, ensure_ascii=False)
            
            # 准备图表数据
            device_names = []
            running_counts = []
            battery_levels = []
            
            # 设备状态数据
            device_status_data = []
            
            # 统计设备状态
            for device in devices:
                # 使用索引访问，兼容SQL Server
                device_id = device[0]
                device_name = device[1]
                device_type = device[2]
                
                device_names.append(device_name)
                
                # 获取设备状态
                status_sql = """
                SELECT * FROM DeviceStatus 
                WHERE DeviceID = ? AND CollectionTime BETWEEN ? AND ? 
                ORDER BY CollectionTime DESC
                """
                status_results = self.db.fetch_all(status_sql, (device_id, start_time, end_time))
                
                # 统计运行状态
                running_count = 0
                total_battery = 0
                valid_battery = 0
                
                if status_results:
                    # 只使用最近10条记录进行统计
                    recent_status = status_results[:10]
                    running_count = sum(1 for s in recent_status if s[3] == '运行正常')
                    battery_levels_list = [s[4] for s in recent_status if s[4] is not None]
                    
                    if battery_levels_list:
                        total_battery = sum(battery_levels_list)
                        valid_battery = len(battery_levels_list)
                        avg_battery = total_battery / valid_battery
                        battery_levels.append(avg_battery)
                    else:
                        battery_levels.append(0)
                else:
                    battery_levels.append(0)
                
                running_counts.append(running_count)
                
                # 保存设备详细状态
                device_status_data.append({
                    "device_id": device_id,
                    "device_name": device_name,
                    "device_type": device_type,
                    "status_count": len(status_results),
                    "running_count": running_count,
                    "avg_battery": battery_levels[-1],
                    "recent_status": status_results[:10]
                })
            
            # 构建图表数据
            chart_data = {
                "labels": device_names,
                "datasets": [
                    {
                        "label": "正常运行次数",
                        "data": running_counts,
                        "backgroundColor": "rgba(75, 192, 192, 0.6)",
                        "borderColor": "rgb(75, 192, 192)",
                        "borderWidth": 1
                    },
                    {
                        "label": "平均电池电量",
                        "data": battery_levels,
                        "backgroundColor": "rgba(153, 102, 255, 0.6)",
                        "borderColor": "rgb(153, 102, 255)",
                        "borderWidth": 1
                    }
                ]
            }
            
            # 构建报表数据
            report_data = {
                "type": "设备状态",
                "region_id": region_id,
                "time_range": f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}",
                "total_devices": len(devices),
                "message": f"共 {len(devices)} 台设备，显示最近10条状态记录",
                "chart_data": chart_data,
                "raw_data": device_status_data
            }
            
            # 返回JSON字符串
            return json.dumps(report_data, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"生成设备状态报表失败: {e}")
            return json.dumps({
                "type": "设备状态",
                "region_id": region_id,
                "time_range": f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}",
                "total_devices": 0,
                "message": f"生成报表失败: {str(e)}",
                "chart_data": {
                    "labels": [],
                    "datasets": []
                },
                "raw_data": []
            }, ensure_ascii=False)
    
    def generate_resource_statistics_report(self, region_id, start_time, end_time):
        """
        生成资源统计报表（JSON格式，支持图表可视化）
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 结构化的报表数据
        """
        import json
        try:
            # 获取林草资源
            resource_sql = "SELECT * FROM ForestResource WHERE RegionID = ?"
            resources = self.db.fetch_all(resource_sql, (region_id,))
            
            # 获取资源变动记录
            change_sql = """
            SELECT * FROM ResourceChangeRecord 
            WHERE resource_id IN (SELECT resource_id FROM ForestResource WHERE RegionID = ?) 
            AND change_time BETWEEN ? AND ? 
            ORDER BY change_time DESC
            """
            changes = self.db.fetch_all(change_sql, (region_id, start_time, end_time))
            
            if not resources and not changes:
                # 返回结构化的空数据
                return json.dumps({
                    "type": "资源统计",
                    "region_id": region_id,
                    "time_range": f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}",
                    "total_resources": 0,
                    "total_area": 0,
                    "message": "该区域没有林草资源记录和资源变动记录。",
                    "chart_data": {
                        "labels": [],
                        "datasets": []
                    },
                    "raw_data": {
                        "resources": [],
                        "changes": []
                    }
                }, ensure_ascii=False)
            
            # 统计资源数据
            total_resources = len(resources)
            total_area = 0
            resource_type_counts = {}
            
            if resources:
                total_area = sum(r[3] for r in resources)  # 使用索引访问，兼容SQL Server
                
                # 统计资源类型分布
                for r in resources:
                    resource_type = r[2]  # 使用索引访问，兼容SQL Server
                    resource_type_counts[resource_type] = resource_type_counts.get(resource_type, 0) + 1
            
            # 准备图表数据
            type_labels = list(resource_type_counts.keys())
            type_counts = list(resource_type_counts.values())
            
            chart_data = {
                "labels": type_labels,
                "datasets": [
                    {
                        "label": "资源数量分布",
                        "data": type_counts,
                        "backgroundColor": [
                            "rgba(255, 99, 132, 0.6)",
                            "rgba(54, 162, 235, 0.6)",
                            "rgba(255, 206, 86, 0.6)",
                            "rgba(75, 192, 192, 0.6)",
                            "rgba(153, 102, 255, 0.6)",
                            "rgba(255, 159, 64, 0.6)"
                        ],
                        "borderColor": [
                            "rgba(255, 99, 132, 1)",
                            "rgba(54, 162, 235, 1)",
                            "rgba(255, 206, 86, 1)",
                            "rgba(75, 192, 192, 1)",
                            "rgba(153, 102, 255, 1)",
                            "rgba(255, 159, 64, 1)"
                        ],
                        "borderWidth": 1
                    }
                ]
            }
            
            # 构建资源变动记录
            change_records = []
            if changes:
                for change in changes:
                    # 使用索引访问，兼容SQL Server
                    change_records.append({
                        "change_id": change[0],
                        "resource_id": change[1],
                        "change_type": change[2],
                        "change_reason": change[3],
                        "change_time": change[4]
                    })
            
            # 构建报表数据
            report_data = {
                "type": "资源统计",
                "region_id": region_id,
                "time_range": f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}",
                "total_resources": total_resources,
                "total_area": round(total_area, 2),
                "resource_types": type_labels,
                "message": f"共 {total_resources} 个资源，总面积 {round(total_area, 2)} 平方公里",
                "chart_data": chart_data,
                "raw_data": {
                    "resources": resources,
                    "changes": change_records
                }
            }
            
            # 返回JSON字符串
            return json.dumps(report_data, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"生成资源统计报表失败: {e}")
            return json.dumps({
                "type": "资源统计",
                "region_id": region_id,
                "time_range": f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}",
                "total_resources": 0,
                "total_area": 0,
                "message": f"生成报表失败: {str(e)}",
                "chart_data": {
                    "labels": [],
                    "datasets": []
                },
                "raw_data": {
                    "resources": [],
                    "changes": []
                }
            }, ensure_ascii=False)
    
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
                conditions.append("gr.RegionID = ?")
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
                # 检查报表名称是否以[已发布]开头，确定发布状态
                is_published = result[1].startswith('[已发布]')
                # 如果已发布，使用生成时间作为发布时间
                publish_time = result[8] if is_published else None
                
                generated_reports.append({
                    'report_id': result[0],
                    'report_name': result[1],
                    'template_id': result[2],
                    'template_name': result[10],  # rt.ReportName - 索引10
                    'report_type': result[11],     # rt.ReportType - 索引11
                    'RegionID': result[3],
                    'start_time': result[4],
                    'end_time': result[5],
                    'report_content': result[6],
                    'report_file_path': result[7],
                    'generated_time': result[8],
                    'generated_by': result[9],
                    'IsPublished': is_published,  # 前端需要的发布状态字段
                    'PublishTime': publish_time  # 前端需要的发布时间字段
                })
            return generated_reports
        except Exception as e:
            print(f"获取生成的报表列表失败: {e}")
            return []
