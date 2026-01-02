from modules.base_module import BaseModule
import datetime

class EquipmentManagementModule(BaseModule):
    """
    设备管理业务线模块
    """
    def __init__(self, db_connection):
        """
        初始化设备管理模块
        :param db_connection: 数据库连接对象
        """
        super().__init__(db_connection)
    
    def create_tables(self):
        """
        创建设备管理相关表
        :return: 是否创建成功
        """
        sql_files = [
            'sql_files/basic_tables.sql',
            'sql_files/equipment_management.sql'
        ]
        
        for sql_file in sql_files:
            if not self.execute_sql_file(sql_file):
                return False
        return True
    
    def add_device_archive(self, device_name, device_type, model_specification, purchase_time, region_id, installer_id, warranty_period):
        """
        添加设备档案
        :param device_name: 设备名称
        :param device_type: 设备类型
        :param model_specification: 型号规格
        :param purchase_time: 采购时间
        :param region_id: 区域ID
        :param installer_id: 安装人员ID
        :param warranty_period: 质保期
        :return: 设备ID
        """
        try:
            device_id = self.generate_id("DEV")
            sql = """
            INSERT INTO DeviceArchive (DeviceID, DeviceName, DeviceType, ModelSpecification, PurchaseTime, RegionID, InstallerID, WarrantyPeriod)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (device_id, device_name, device_type, model_specification, purchase_time, region_id, installer_id, warranty_period)
            if self.db.execute(sql, params):
                return device_id
            return None
        except Exception as e:
            print(f"添加设备档案失败: {e}")
            return None
    
    def get_device_archives(self, region_id=None, device_type=None):
        """
        获取设备档案列表
        :param region_id: 区域ID（可选）
        :param device_type: 设备类型（可选）
        :return: 设备档案列表
        """
        try:
            conditions = []
            params = []
            
            # 只有当region_id不为None且不为空字符串时才添加条件
            if region_id is not None and region_id != "":
                conditions.append("RegionID = ?")
                params.append(region_id)
            # 只有当device_type不为None且不为空字符串时才添加条件
            if device_type is not None and device_type != "":
                conditions.append("DeviceType = ?")
                params.append(device_type)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM DeviceArchive{where_clause} ORDER BY PurchaseTime DESC"
            
            results = self.db.fetch_all(sql, params)
            devices = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                devices.append({
                    'DeviceID': result[0],
                    'DeviceName': result[1],
                    'DeviceType': result[2],
                    'ModelSpecification': result[3],
                    'PurchaseTime': result[4],
                    'RegionID': result[5],
                    'InstallerID': result[6],
                    'WarrantyPeriod': result[7]
                })
            return devices
        except Exception as e:
            print(f"获取设备档案失败: {e}")
            return []
    
    def add_device_status(self, device_id, running_status, battery_level=None, signal_strength=None):
        """
        添加设备状态
        :param device_id: 设备ID
        :param running_status: 运行状态
        :param battery_level: 电池电量
        :param signal_strength: 信号强度
        :return: 状态ID
        """
        try:
            status_id = self.generate_id("STAT")
            collection_time = datetime.datetime.now()
            sql = """
            INSERT INTO DeviceStatus (StatusID, DeviceID, CollectionTime, RunningStatus, BatteryLevel, SignalStrength)
            VALUES (?, ?, GETDATE(), ?, ?, ?)
            """
            params = (status_id, device_id, collection_time, running_status, battery_level, signal_strength)
            if self.db.execute(sql, params):
                return status_id
            return None
        except Exception as e:
            print(f"添加设备状态失败: {e}")
            return None
    
    def get_device_status(self, device_id, start_time=None, end_time=None):
        """
        获取设备状态记录
        :param device_id: 设备ID
        :param start_time: 开始时间（可选）
        :param end_time: 结束时间（可选）
        :return: 设备状态记录列表
        """
        try:
            conditions = ["DeviceID = ?"]
            params = [device_id]
            
            if start_time:
                conditions.append("CollectionTime >= ?")
                params.append(start_time)
            if end_time:
                conditions.append("CollectionTime <= ?")
                params.append(end_time)
            
            where_clause = " WHERE " + " AND ".join(conditions)
            sql = f"SELECT * FROM DeviceStatus{where_clause} ORDER BY CollectionTime DESC"
            
            results = self.db.fetch_all(sql, params)
            status_records = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                status_records.append({
                    'StatusID': result[0],
                    'DeviceID': result[1],
                    'CollectionTime': result[2],
                    'RunningStatus': result[3],
                    'BatteryLevel': result[4],
                    'SignalStrength': result[5]
                })
            return status_records
        except Exception as e:
            print(f"获取设备状态失败: {e}")
            return []
    
    def add_equipment_inspection(self, device_id, inspection_time, inspector_id, maintenance_type, inspection_result, problem_description=None, maintenance_content=None, maintenance_result=None):
        """
        添加设备巡检记录
        :param device_id: 设备ID
        :param inspection_time: 巡检时间
        :param inspector_id: 巡检人员ID
        :param maintenance_type: 维护类型
        :param inspection_result: 巡检结果
        :param problem_description: 问题描述（可选）
        :param maintenance_content: 维护内容（可选）
        :param maintenance_result: 维护结果（可选）
        :return: 巡检ID
        """
        try:
            inspection_id = self.generate_id("INSP")
            sql = """
            INSERT INTO EquipmentInspection (InspectionID, device_id, InspectionTime, InspectorID, MaintenanceType, InspectionResult, ProblemDescription, MaintenanceContent, MaintenanceResult)
            VALUES (?, ?, GETDATE(), ?, ?, ?, ?, ?, ?)
            """
            params = (inspection_id, device_id, inspection_time, inspector_id, maintenance_type, inspection_result, problem_description, maintenance_content, maintenance_result)
            if self.db.execute(sql, params):
                return inspection_id
            return None
        except Exception as e:
            print(f"添加设备巡检记录失败: {e}")
            return None
    
    def get_equipment_inspections(self, device_id=None, inspector_id=None):
        """
        获取设备巡检记录
        :param device_id: 设备ID（可选）
        :param inspector_id: 巡检人员ID（可选）
        :return: 设备巡检记录列表
        """
        try:
            conditions = []
            params = []
            
            if device_id:
                conditions.append("device_id = ?")
                params.append(device_id)
            if inspector_id:
                conditions.append("InspectorID = ?")
                params.append(inspector_id)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM EquipmentInspection{where_clause} ORDER BY InspectionTime DESC"
            
            results = self.db.fetch_all(sql, params)
            inspections = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                inspections.append({
                    'InspectionID': result[0],
                    'device_id': result[1],
                    'InspectionTime': result[2],
                    'InspectorID': result[3],
                    'MaintenanceType': result[4],
                    'InspectionResult': result[5],
                    'ProblemDescription': result[6],
                    'MaintenanceContent': result[7],
                    'MaintenanceResult': result[8]
                })
            return inspections
        except Exception as e:
            print(f"获取设备巡检记录失败: {e}")
            return []
