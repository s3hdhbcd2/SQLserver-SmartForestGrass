from modules.base_module import BaseModule
import datetime

class ResourceManagementModule(BaseModule):
    """
    资源管理业务线模块
    """
    def __init__(self, db_connection):
        """
        初始化资源管理模块
        :param db_connection: 数据库连接对象
        """
        super().__init__(db_connection)
    
    def create_tables(self):
        """
        创建资源管理相关表
        :return: 是否创建成功
        """
        sql_files = [
            'sql_files/basic_tables.sql',
            'sql_files/resource_management.sql'
        ]
        
        for sql_file in sql_files:
            if not self.execute_sql_file(sql_file):
                return False
        return True
    
    def add_forest_resource(self, region_id, resource_type, coverage_area, tree_species, growth_status, updated_by):
        """
        添加林草资源
        :param region_id: 区域ID
        :param resource_type: 资源类型
        :param coverage_area: 覆盖面积
        :param tree_species: 树种
        :param growth_status: 生长状态
        :param updated_by: 更新人ID
        :return: 资源ID
        """
        try:
            resource_id = self.generate_id("RES")
            update_time = datetime.datetime.now()
            
            sql = """
            INSERT INTO ForestResource (ResourceID, region_id, ResourceType, CoverageArea, TreeSpecies, GrowthStatus, UpdateTime, UpdatedBy)
            VALUES (?, ?, ?, ?, ?, ?, GETDATE(), ?)
            """
            params = (resource_id, region_id, resource_type, coverage_area, tree_species, growth_status, update_time, updated_by)
            if self.db.execute(sql, params):
                return resource_id
            return None
        except Exception as e:
            print(f"添加林草资源失败: {e}")
            return None
    
    def update_forest_resource(self, resource_id, coverage_area=None, tree_species=None, growth_status=None, updated_by=None):
        """
        更新林草资源
        :param resource_id: 资源ID
        :param coverage_area: 覆盖面积（可选）
        :param tree_species: 树种（可选）
        :param growth_status: 生长状态（可选）
        :param updated_by: 更新人ID（可选）
        :return: 是否更新成功
        """
        try:
            update_fields = []
            params = []
            
            if coverage_area is not None:
                update_fields.append("coverage_area = ?")
                params.append(coverage_area)
            if tree_species is not None:
                update_fields.append("tree_species = ?")
                params.append(tree_species)
            if growth_status is not None:
                update_fields.append("growth_status = ?")
                params.append(growth_status)
            
            # 总是更新时间
            update_fields.append("update_time = ?")
            params.append(datetime.datetime.now())
            
            if updated_by is not None:
                update_fields.append("updated_by = ?")
                params.append(updated_by)
            
            if not update_fields:
                return False
            
            sql = f"""
            UPDATE ForestResource 
            SET {', '.join(update_fields)} 
            WHERE ResourceID = ?
            """
            params.append(resource_id)
            
            return self.db.execute(sql, params)
        except Exception as e:
            print(f"更新林草资源失败: {e}")
            return False
    
    def get_forest_resources(self, region_id=None):
        """
        获取林草资源列表
        :param region_id: 区域ID（可选）
        :return: 林草资源列表
        """
        try:
            conditions = []
            params = []
            
            if region_id:
                conditions.append("region_id = ?")
                params.append(region_id)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM ForestResource{where_clause} ORDER BY UpdateTime DESC"
            
            results = self.db.fetch_all(sql, params)
            resources = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                resources.append({
                    'resource_id': result[0],
                    'region_id': result[1],
                    'resource_type': result[2],
                    'tree_species': result[3],
                    'quantity': result[4],
                    'coverage_area': result[5],
                    'growth_status': result[6],
                    'planting_time': result[7],
                    'update_time': result[8],
                    'updated_by': result[9]
                })
            return resources
        except Exception as e:
            print(f"获取林草资源失败: {e}")
            return []
    
    def add_resource_change_record(self, resource_id, change_type, change_reason, change_time, operator_id):
        """
        添加资源变动记录
        :param resource_id: 资源ID
        :param change_type: 变动类型
        :param change_reason: 变动原因
        :param change_time: 变动时间
        :param operator_id: 操作人ID
        :return: 变动ID
        """
        try:
            change_id = self.generate_id("CHG")
            sql = """
            INSERT INTO ResourceChangeRecord (ChangeID, ResourceID, ChangeType, ChangeReason, ChangeTime, OperatorID)
            VALUES (?, ?, ?, ?, GETDATE(), ?)
            """
            params = (change_id, resource_id, change_type, change_reason, change_time, operator_id)
            if self.db.execute(sql, params):
                return change_id
            return None
        except Exception as e:
            print(f"添加资源变动记录失败: {e}")
            return None
    
    def get_resource_change_records(self, resource_id=None):
        """
        获取资源变动记录
        :param resource_id: 资源ID（可选）
        :return: 资源变动记录列表
        """
        try:
            conditions = []
            params = []
            
            if resource_id:
                conditions.append("ResourceID = ?")
                params.append(resource_id)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT * FROM ResourceChangeRecord{where_clause} ORDER BY ChangeTime DESC"
            
            results = self.db.fetch_all(sql, params)
            change_records = []
            for result in results:
                # 使用索引访问，兼容SQL Server
                change_records.append({
                    'change_id': result[0],
                    'resource_id': result[1],
                    'change_type': result[2],
                    'change_reason': result[3],
                    'change_time': result[4],
                    'operator_id': result[5]
                })
            return change_records
        except Exception as e:
            print(f"获取资源变动记录失败: {e}")
            return []
