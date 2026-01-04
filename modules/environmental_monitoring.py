from modules.base_module import BaseModule
import datetime

class EnvironmentalMonitoringModule(BaseModule):
    """
    环境监测业务线模块
    """
    def __init__(self, db_connection):
        """
        初始化环境监测模块
        :param db_connection: 数据库连接对象
        """
        super().__init__(db_connection)
    
    def create_tables(self):
        """
        创建环境监测相关表
        :return: 是否创建成功
        """
        sql_files = [
            'sql_files/basic_tables.sql',
            'sql_files/environmental_monitoring.sql'
        ]
        
        for sql_file in sql_files:
            if not self.execute_sql_file(sql_file):
                return False
        return True
    
    def add_sensor(self, region_id, device_model, monitoring_type, install_time, communication_protocol):
        """添加传感器
        :param region_id: 区域ID
        :param device_model: 设备型号
        :param monitoring_type: 监测类型
        :param install_time: 安装时间
        :param communication_protocol: 通信协议
        :return: 传感器ID
        """
        try:
            sensor_id = f"S{int(time.time())}"
            sql = """
            INSERT INTO Sensor (SensorID, RegionID, DeviceModel, MonitoringType, InstallTime, CommunicationProtocol)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (sensor_id, region_id, device_model, monitoring_type, install_time, communication_protocol)
            if self.db.execute(sql, params):
                return sensor_id
            return None
        except Exception as e:
            print(f"添加传感器失败: {e}")
            return None
    
    def get_sensors(self, region_id=None):
        """
        获取传感器列表
        :param region_id: 区域ID（可选）
        :return: 传感器列表
        """
        try:
            conditions = []
            params = []
            
            if region_id:
                conditions.append("RegionID = ?")
                params.append(region_id)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM Sensor{where_clause} ORDER BY InstallTime DESC"
            
            results = self.db.fetch_all(sql, params)
            sensors = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                sensors.append({
                    'sensor_id': result[0],
                    'RegionID': result[1],
                    'device_model': result[2],
                    'monitoring_type': result[3],
                    'install_time': result[4],
                    'communication_protocol': result[5]
                })
            return sensors
        except Exception as e:
            print(f"获取传感器列表失败: {e}")
            return []
    
    def add_monitoring_data(self, sensor_id, region_id, data_time, temperature=None, humidity=None, 
                          wind_speed=None, rainfall=None, pest_disease_value=None, 
                          smoke_value=None, soil_moisture=None, image_path=None):
        """
        添加监测数据
        :param sensor_id: 传感器ID
        :param region_id: 区域ID
        :param data_time: 数据时间
        :param temperature: 温度
        :param humidity: 湿度
        :param wind_speed: 风速
        :param rainfall: 降雨量
        :param pest_disease_value: 病虫害指数
        :param smoke_value: 烟雾值
        :param soil_moisture: 土壤湿度
        :param image_path: 图像路径
        :return: 数据ID
        """
        try:
            data_id = self.generate_id("DATA")
            sql = """
            INSERT INTO MonitoringData (DataID, SensorID, RegionID, DataTime, Temperature, Humidity, 
                                     WindSpeed, Rainfall, PestDiseaseValue, SmokeValue, 
                                     SoilMoisture, ImagePath, DataStatus)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '有效')
            """
            params = (data_id, sensor_id, region_id, data_time, temperature, humidity, 
                     wind_speed, rainfall, pest_disease_value, smoke_value, 
                     soil_moisture, image_path)
            if self.db.execute(sql, params):
                return data_id
            return None
        except Exception as e:
            print(f"添加监测数据失败: {e}")
            return None
    
    def get_monitoring_data_by_area(self, region_id, start_time, end_time):
        """按区域获取监测数据
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 监测数据列表
        """
        try:
            # 根据region_id是否为空，构建不同的SQL查询
            if region_id is None or region_id == "":
                # 查询所有区域的数据
                sql = """
                SELECT * FROM MonitoringData 
                WHERE DataTime BETWEEN ? AND ? 
                ORDER BY DataTime DESC
                """
                params = (start_time, end_time)
            else:
                # 查询特定区域的数据
                sql = """
                SELECT * FROM MonitoringData 
                WHERE RegionID = ? AND DataTime BETWEEN ? AND ? 
                ORDER BY DataTime DESC
                """
                params = (region_id, start_time, end_time)
            results = self.db.fetch_all(sql, params)
            
            monitor_data = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                monitor_data.append({
                    'DataID': result[0],
                    'SensorID': result[1],
                    'RegionID': result[2],
                    'DataTime': result[3],
                    'Temperature': result[4],
                    'Humidity': result[5],
                    'WindSpeed': result[6],
                    'Rainfall': result[7],
                    'PestDiseaseValue': result[8],
                    'SmokeValue': result[9],
                    'SoilMoisture': result[10],
                    'ImagePath': result[11],
                    'DataStatus': result[12]
                })
            return monitor_data
        except Exception as e:
            print(f"获取监测数据失败: {e}")
            return []
