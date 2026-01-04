import datetime

class BaseModule:
    """
    基础模块，包含所有业务线共享的功能
    """
    def __init__(self, db_connection):
        """
        初始化基础模块
        :param db_connection: 数据库连接对象
        """
        self.db = db_connection
    
    def generate_id(self, prefix):
        """
        生成唯一ID（格式与现有数据一致，在现有基础上递增）
        :param prefix: ID前缀
        :return: 唯一ID字符串
        """
        # 定义不同前缀对应的ID格式和表名
        id_formats = {
            'RULE': { 'table': 'WarningRule', 'column': 'RuleID', 'format': 'WR000' },
            'WARN': { 'table': 'WarningRecord', 'column': 'WarningID', 'format': 'WRC0000' },
            'NOTI': { 'table': 'NotificationRecord', 'column': 'NotificationID', 'format': 'NOTI0000' },
            'DEV': { 'table': 'DeviceArchive', 'column': 'DeviceID', 'format': 'D0000' },
            'EI': { 'table': 'EquipmentInspection', 'column': 'InspectionID', 'format': 'EI0000' },
            'FR': { 'table': 'ForestResource', 'column': 'ResourceID', 'format': 'FR000' },
            'RCR': { 'table': 'ResourceChangeRecord', 'column': 'ChangeID', 'format': 'RCR0000' },
            'GR': { 'table': 'GeneratedReport', 'column': 'ReportID', 'format': 'GR0000' }
        }
        
        # 如果是已知前缀，生成与现有格式一致的ID
        if prefix in id_formats:
            format_info = id_formats[prefix]
            table = format_info['table']
            column = format_info['column']
            format_str = format_info['format']
            
            try:
                # 查询所有设备ID，找出最大的数字部分
                sql = f"SELECT {column} FROM {table}"
                all_ids = self.db.fetch_all(sql)
                
                if all_ids:
                    max_num = 0
                    for id_row in all_ids:
                        # 处理数据库返回的pyodbc.Row或tuple类型
                        try:
                            # 尝试使用索引访问，适用于pyodbc.Row和tuple
                            device_id = id_row[0]
                        except (TypeError, IndexError):
                            # 如果无法使用索引访问，则直接使用id_row
                            device_id = id_row
                        
                        # 提取数字部分
                        if prefix == 'GR':
                            # 针对GR前缀的特殊处理：只考虑格式为GRXXXX的ID
                            if device_id.startswith('GR'):
                                # 提取GR前缀后的数字部分
                                num_part = ''.join(filter(str.isdigit, device_id))
                                if num_part:
                                    num = int(num_part)
                                    if num > max_num:
                                        max_num = num
                        elif prefix == 'FR':
                            # 针对FR前缀的特殊处理：只考虑格式为FRXXX的ID
                            if len(device_id) == 5 and device_id.startswith('FR') and device_id[2:].isdigit():
                                # 提取3位数字部分
                                num_part = device_id[2:]
                                if num_part:
                                    num = int(num_part)
                                    if num > max_num:
                                        max_num = num
                        elif prefix == 'RCR':
                            # 针对RCR前缀的特殊处理：只考虑格式为RCRXXXX的ID
                            if len(device_id) == 7 and device_id.startswith('RCR') and device_id[3:].isdigit():
                                # 提取4位数字部分
                                num_part = device_id[3:]
                                if num_part:
                                    num = int(num_part)
                                    if num > max_num:
                                        max_num = num
                        else:
                            # 其他前缀使用原有逻辑
                            num_part = ''.join(filter(str.isdigit, device_id))
                            if num_part:
                                num = int(num_part)
                                if num > max_num:
                                    max_num = num
                    
                    # 递增数字
                    new_num = max_num + 1
                    
                    # 格式化新ID
                    if format_str == 'WR000':
                        # RuleID格式：WR001, WR002...
                        return f"WR{new_num:03d}"
                    elif format_str == 'WRC0000':
                        # WarningID格式：WRC0001, WRC0002...
                        return f"WRC{new_num:04d}"
                    elif format_str == 'NOTI0000':
                        # NotificationID格式：NOTI0001, NOTI0002...
                        return f"NOTI{new_num:04d}"
                    elif format_str == 'D0000':
                        # DeviceID格式：D0001, D0002...
                        return f"D{new_num:04d}"
                    elif format_str == 'EI0000':
                        # InspectionID格式：EI0001, EI0002...
                        return f"EI{new_num:04d}"
                    elif format_str == 'FR000':
                        # ResourceID格式：FR001, FR002...
                        return f"FR{new_num:03d}"
                    elif format_str == 'RCR0000':
                        # ChangeID格式：RCR0001, RCR0002...
                        return f"RCR{new_num:04d}"
                    elif format_str == 'GR0000':
                        # ReportID格式：GR0001, GR0002...
                        return f"GR{new_num:04d}"
            except Exception as e:
                print(f"查询最大ID失败: {e}")
        
        # 如果前缀不在已知列表中，或者查询失败，使用默认格式（确保长度不超过20位）
        timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")  # 12位时间戳
        # 使用正数随机数，避免生成包含'-'的ID
        random_num = str(abs(hash(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))))[:2]  # 2位随机数
        return f"{prefix}{timestamp}{random_num}"  # 前缀+12位时间戳+2位随机数，总长度不超过20位
    
    def execute_sql_file(self, file_path):
        """
        执行SQL文件
        :param file_path: SQL文件路径
        :return: 是否执行成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 只提取SQL Server语句
            sql_statements = self._extract_sqlserver_statements(sql_content)
            
            # 执行SQL语句
            for sql in sql_statements:
                if sql.strip():
                    if not self.db.execute_script(sql):
                        return False
            
            return True
        except Exception as e:
            print(f"执行SQL文件失败: {e}")
            return False
    
    def _extract_sqlserver_statements(self, sql_content):
        """
        从SQL文件中提取SQL Server语句
        :param sql_content: SQL文件内容
        :return: SQL Server语句列表
        """
        lines = sql_content.split('\n')
        in_sqlserver_block = False
        sqlserver_sql = []
        current_statement = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('-- SQL Server版本'):
                in_sqlserver_block = True
                if current_statement:
                    sqlserver_sql.append('\n'.join(current_statement))
                    current_statement = []
            elif line.startswith('-- SQLite版本'):
                in_sqlserver_block = False
                if current_statement:
                    sqlserver_sql.append('\n'.join(current_statement))
                    current_statement = []
            elif in_sqlserver_block and line:
                current_statement.append(line)
        
        if current_statement:
            sqlserver_sql.append('\n'.join(current_statement))
        
        return sqlserver_sql
    
    def _extract_sqlite_statements(self, sql_content):
        """
        从SQL文件中提取SQLite语句
        :param sql_content: SQL文件内容
        :return: SQLite语句列表
        """
        lines = sql_content.split('\n')
        in_sqlite_block = False
        sqlite_sql = []
        current_statement = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('-- SQLite版本'):
                in_sqlite_block = True
                if current_statement:
                    sqlite_sql.append('\n'.join(current_statement))
                    current_statement = []
            elif line.startswith('-- SQL Server版本'):
                in_sqlite_block = False
                if current_statement:
                    sqlite_sql.append('\n'.join(current_statement))
                    current_statement = []
            elif line.startswith('--') and not line.startswith('-- SQLite版本'):
                # 跳过其他注释
                continue
            elif in_sqlite_block:
                if line.endswith(';'):
                    current_statement.append(line)
                    sqlite_sql.append('\n'.join(current_statement))
                    current_statement = []
                elif line:
                    current_statement.append(line)
        
        if current_statement:
            sqlite_sql.append('\n'.join(current_statement))
        
        return sqlite_sql
