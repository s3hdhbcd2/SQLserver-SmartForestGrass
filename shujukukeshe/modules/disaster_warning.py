from modules.base_module import BaseModule
import datetime

class DisasterWarningModule(BaseModule):
    """
    灾害预警业务线模块
    """
    def __init__(self, db_connection):
        """
        初始化灾害预警模块
        :param db_connection: 数据库连接对象
        """
        super().__init__(db_connection)
    
    def create_tables(self):
        """
        创建灾害预警相关表
        :return: 是否创建成功
        """
        sql_files = [
            'sql_files/basic_tables.sql',
            'sql_files/environmental_monitoring.sql',
            'sql_files/disaster_warning.sql'
        ]
        
        for sql_file in sql_files:
            if not self.execute_sql_file(sql_file):
                return False
        return True
    
    def add_warning_rule(self, warning_type, trigger_condition, warning_level, is_active=1):
        """
        添加预警规则
        :param warning_type: 预警类型
        :param trigger_condition: 触发条件
        :param warning_level: 预警级别
        :param is_active: 是否生效
        :return: 规则ID
        """
        try:
            rule_id = self.generate_id("RULE")
            sql = """
            INSERT INTO WarningRule (RuleID, WarningType, TriggerCondition, WarningLevel, IsActive)
            VALUES (?, ?, ?, ?, ?)
            """
            params = (rule_id, warning_type, trigger_condition, warning_level, is_active)
            if self.db.execute(sql, params):
                return rule_id
            return None
        except Exception as e:
            print(f"添加预警规则失败: {e}")
            return None
    
    def get_warning_rules(self, warning_type=None):
        """
        获取预警规则列表
        :param warning_type: 预警类型（可选）
        :return: 预警规则列表
        """
        try:
            conditions = []
            params = []
            
            if warning_type:
                conditions.append("WarningType = ?")
                params.append(warning_type)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM WarningRule{where_clause} ORDER BY WarningType"
            
            results = self.db.fetch_all(sql, params)
            rules = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                rules.append({
                    'RuleID': result[0],
                    'WarningType': result[1],
                    'TriggerCondition': result[2],
                    'WarningLevel': result[3],
                    'IsActive': result[4]
                })
            return rules
        except Exception as e:
            print(f"获取预警规则失败: {e}")
            return []
    
    def add_warning_record(self, rule_id, region_id, trigger_time, warning_content, status='未处理', handler_id=None, handle_result=None):
        """
        添加预警记录
        :param rule_id: 规则ID
        :param region_id: 区域ID
        :param trigger_time: 触发时间
        :param warning_content: 预警内容
        :param status: 处理状态
        :param handler_id: 处理人ID
        :param handle_result: 处理结果
        :return: 预警ID
        """
        try:
            warning_id = self.generate_id("WARN")
            sql = """
            INSERT INTO WarningRecord (WarningID, RuleID, region_id, TriggerTime, WarningContent, Status, HandlerID, HandleResult)
            VALUES (?, ?, ?, GETDATE(), ?, ?, ?, ?)
            """
            params = (warning_id, rule_id, region_id, trigger_time, warning_content, status, handler_id, handle_result)
            if self.db.execute(sql, params):
                return warning_id
            return None
        except Exception as e:
            print(f"添加预警记录失败: {e}")
            return None
    
    def update_warning_status(self, warning_id, status, handler_id, handle_result=None):
        """
        更新预警状态
        :param warning_id: 预警ID
        :param status: 处理状态
        :param handler_id: 处理人ID
        :param handle_result: 处理结果
        :return: 是否更新成功
        """
        try:
            sql = """
            UPDATE WarningRecord 
            SET Status = ?, HandlerID = ?, HandleResult = ? 
            WHERE WarningID = ?
            """
            params = (status, handler_id, handle_result, warning_id)
            return self.db.execute(sql, params)
        except Exception as e:
            print(f"更新预警状态失败: {e}")
            return False
    
    def get_warnings_by_area(self, region_id):
        """
        按区域获取预警记录
        :param region_id: 区域ID
        :return: 预警记录列表
        """
        try:
            sql = """
            SELECT * FROM WarningRecord
            WHERE region_id = ? 
            ORDER BY TriggerTime DESC
            """
            params = (region_id,)
            results = self.db.fetch_all(sql, params)
            
            warnings = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                warnings.append({
                    'WarningID': result[0],
                    'RuleID': result[1],
                    'region_id': result[2],
                    'TriggerTime': result[3],
                    'WarningContent': result[4],
                    'Status': result[5],
                    'HandlerID': result[6],
                    'HandleResult': result[7]
                })
            return warnings
        except Exception as e:
            print(f"获取预警记录失败: {e}")
            return []
    
    def add_notification_record(self, warning_id, receiver_id, notification_method, send_time, receive_status='已发送'):
        """
        添加通知记录
        :param warning_id: 预警ID
        :param receiver_id: 接收人ID
        :param notification_method: 通知方式
        :param send_time: 发送时间
        :param receive_status: 接收状态
        :return: 通知ID
        """
        try:
            notification_id = self.generate_id("NOTI")
            sql = """
            INSERT INTO NotificationRecord (NotificationID, WarningID, ReceiverID, NotificationMethod, SendTime, ReceiveStatus)
            VALUES (?, ?, ?, ?, GETDATE(), ?)
            """
            params = (notification_id, warning_id, receiver_id, notification_method, send_time, receive_status)
            if self.db.execute(sql, params):
                return notification_id
            return None
        except Exception as e:
            print(f"添加通知记录失败: {e}")
            return None
