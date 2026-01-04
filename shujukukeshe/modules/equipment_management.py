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
    
    def get_device_archives(self, region_id=None, device_type=None, status=None):
        """
        获取设备档案列表，包含最新的设备状态
        :param region_id: 区域ID（可选）
        :param device_type: 设备类型（可选）
        :param status: 设备状态（可选）
        :return: 设备档案列表
        """
        try:
            conditions = []
            params = []
            
            # 只有当region_id不为None且不为空字符串时才添加条件
            if region_id is not None and region_id != "":
                conditions.append("da.RegionID = ?")
                params.append(region_id)
            # 只有当device_type不为None且不为空字符串时才添加条件
            if device_type is not None and device_type != "":
                conditions.append("da.DeviceType = ?")
                params.append(device_type)
            # 只有当status不为None且不为空字符串时才添加条件
            if status is not None and status != "":
                conditions.append("ISNULL(ds.RunningStatus, '正常') = ?")
                params.append(status)
            
            # 使用LEFT JOIN获取最新的设备状态
            sql = f"""
            SELECT 
                da.*,
                ISNULL(ds.RunningStatus, '正常') as Status
            FROM DeviceArchive da
            LEFT JOIN (
                SELECT 
                    DeviceID,
                    RunningStatus
                FROM (
                    SELECT 
                        DeviceID,
                        RunningStatus,
                        ROW_NUMBER() OVER (PARTITION BY DeviceID ORDER BY CollectionTime DESC) as rn
                    FROM DeviceStatus
                ) t
                WHERE t.rn = 1
            ) ds ON da.DeviceID = ds.DeviceID
            """
            
            # 添加WHERE子句
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            sql += " ORDER BY da.PurchaseTime DESC"
            
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
                    'WarrantyPeriod': result[7],
                    'Status': result[8] if len(result) > 8 else '正常'  # 设备状态
                })
            return devices
        except Exception as e:
            print(f"获取设备档案失败: {e}")
            return []
    
    def update_device_archive(self, device_id, device_name, device_type, model_specification, region_id, equipment_status, purchase_time=None, warranty_period=None):
        """
        更新设备档案
        :param device_id: 设备ID
        :param device_name: 设备名称
        :param device_type: 设备类型
        :param model_specification: 型号规格
        :param region_id: 区域ID
        :param equipment_status: 设备状态
        :param purchase_time: 购买时间（可选）
        :param warranty_period: 质保期（可选）
        :return: 是否更新成功
        """
        try:
            # 更新设备档案
            if purchase_time and warranty_period:
                sql = """
                UPDATE DeviceArchive 
                SET DeviceName = ?, DeviceType = ?, ModelSpecification = ?, RegionID = ?, PurchaseTime = ?, WarrantyPeriod = ?
                WHERE DeviceID = ?
                """
                params = (device_name, device_type, model_specification, region_id, purchase_time, warranty_period, device_id)
            elif purchase_time:
                sql = """
                UPDATE DeviceArchive 
                SET DeviceName = ?, DeviceType = ?, ModelSpecification = ?, RegionID = ?, PurchaseTime = ?
                WHERE DeviceID = ?
                """
                params = (device_name, device_type, model_specification, region_id, purchase_time, device_id)
            elif warranty_period:
                sql = """
                UPDATE DeviceArchive 
                SET DeviceName = ?, DeviceType = ?, ModelSpecification = ?, RegionID = ?, WarrantyPeriod = ?
                WHERE DeviceID = ?
                """
                params = (device_name, device_type, model_specification, region_id, warranty_period, device_id)
            else:
                sql = """
                UPDATE DeviceArchive 
                SET DeviceName = ?, DeviceType = ?, ModelSpecification = ?, RegionID = ?
                WHERE DeviceID = ?
                """
                params = (device_name, device_type, model_specification, region_id, device_id)
            
            if not self.db.execute(sql, params):
                return False
            
            # 同时更新设备状态 - 只有当equipment_status不为None时才更新
            if equipment_status:
                status_id = self.add_device_status(
                    device_id=device_id,
                    running_status=equipment_status,
                    battery_level=100,
                    signal_strength=100
                )
                if not status_id:
                    return False
            
            return True
        except Exception as e:
            print(f"更新设备档案失败: {e}")
            return False
    
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
            # 使用DS前缀生成状态ID，与现有数据格式保持一致
            status_id = self.generate_id("DS")
            collection_time = datetime.datetime.now()
            sql = """
            INSERT INTO DeviceStatus (StatusID, DeviceID, CollectionTime, RunningStatus, BatteryLevel, SignalStrength)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (status_id, device_id, collection_time, running_status, battery_level, signal_strength)
            print(f"添加设备状态SQL: {sql}")
            print(f"参数: {params}")
            if self.db.execute(sql, params):
                print(f"设备状态添加成功，ID: {status_id}")
                return status_id
            else:
                print("设备状态添加失败，execute返回False")
                return None
        except Exception as e:
            print(f"添加设备状态失败: {e}")
            import traceback
            traceback.print_exc()
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
            
            print(f"查询设备状态，设备ID: {device_id}")
            print(f"开始时间: {start_time}, 结束时间: {end_time}")
            
            if start_time:
                conditions.append("CollectionTime >= ?")
                params.append(start_time)
            if end_time:
                conditions.append("CollectionTime <= ?")
                params.append(end_time)
            
            where_clause = " WHERE " + " AND ".join(conditions)
            sql = f"SELECT * FROM DeviceStatus{where_clause} ORDER BY CollectionTime DESC"
            
            print(f"执行SQL: {sql}")
            print(f"参数: {params}")
            
            results = self.db.fetch_all(sql, params)
            print(f"查询结果数量: {len(results)}")
            
            status_records = []
            for result in results:
                print(f"原始结果: {result}")
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
            import traceback
            traceback.print_exc()
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
            inspection_id = self.generate_id("EI")
            sql = """
            INSERT INTO EquipmentInspection (InspectionID, DeviceID, InspectionTime, InspectorID, MaintenanceType, InspectionResult, ProblemDescription, MaintenanceContent, MaintenanceResult)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (inspection_id, device_id, inspection_time, inspector_id, maintenance_type, inspection_result, problem_description, maintenance_content, maintenance_result)
            if self.db.execute(sql, params):
                # 根据巡检结果直接更新设备状态，不再考虑维护结果
                if inspection_result == "正常":
                    # 如果巡检结果正常，设备状态设置为正常
                    self.add_device_status(device_id, "正常")
                elif inspection_result == "异常":
                    # 如果巡检结果异常，设备状态设置为异常
                    self.add_device_status(device_id, "异常")
                elif inspection_result == "故障":
                    # 如果巡检结果为故障，设备状态设置为故障
                    self.add_device_status(device_id, "故障")
                return inspection_id
            return None
        except Exception as e:
            print(f"添加设备巡检记录失败: {e}")
            return None
    
    def get_equipment_inspections(self, device_id=None, inspector_id=None, audit_status=None):
        """
        获取设备巡检记录
        :param device_id: 设备ID（可选）
        :param inspector_id: 巡检人员ID（可选）
        :param audit_status: 审核状态（可选）
        :return: 设备巡检记录列表
        """
        try:
            conditions = []
            params = []
            
            if device_id:
                conditions.append("DeviceID = ?")
                params.append(device_id)
            if inspector_id:
                conditions.append("InspectorID = ?")
                params.append(inspector_id)
            if audit_status:
                conditions.append("AuditStatus = ?")
                params.append(audit_status)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM EquipmentInspection{where_clause} ORDER BY InspectionTime DESC"
            
            results = self.db.fetch_all(sql, params)
            inspections = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                inspections.append({
                    'InspectionID': result[0],
                    'DeviceID': result[1],
                    'InspectionTime': result[2],
                    'InspectorID': result[3],
                    'MaintenanceType': result[4],
                    'InspectionResult': result[5],
                    'ProblemDescription': result[6],
                    'MaintenanceContent': result[7],
                    'MaintenanceResult': result[8],
                    'AuditStatus': result[9],
                    'AuditorID': result[10],
                    'AuditTime': result[11],
                    'AuditComments': result[12]
                })
            return inspections
        except Exception as e:
            print(f"获取设备巡检记录失败: {e}")
            return []
    
    def audit_equipment_inspection(self, inspection_id, audit_status, auditor_id, audit_comments=None):
        """
        审核设备巡检记录
        :param inspection_id: 巡检记录ID
        :param audit_status: 审核状态（通过/拒绝）
        :param auditor_id: 审核人ID
        :param audit_comments: 审核意见
        :return: 是否审核成功
        """
        try:
            sql = """
            UPDATE EquipmentInspection 
            SET AuditStatus = ?, AuditorID = ?, AuditTime = GETDATE(), AuditComments = ?
            WHERE InspectionID = ?
            """
            params = (audit_status, auditor_id, audit_comments, inspection_id)
            return self.db.execute(sql, params)
        except Exception as e:
            print(f"审核设备巡检记录失败: {e}")
            return False
