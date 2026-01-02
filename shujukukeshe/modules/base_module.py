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
            'DEV': { 'table': 'DeviceArchive', 'column': 'DeviceID', 'format': 'DEV0000' }
        }
        
        # 如果是已知前缀，生成与现有格式一致的ID
        if prefix in id_formats:
            format_info = id_formats[prefix]
            table = format_info['table']
            column = format_info['column']
            format_str = format_info['format']
            
            try:
                # 查询现有最大ID
                sql = f"SELECT MAX({column}) FROM {table}"
                max_id = self.db.fetch_one(sql)
                max_id = max_id[0] if max_id else None
                
                if max_id:
                    # 提取数字部分
                    num_part = ''.join(filter(str.isdigit, max_id))
                    if num_part:
                        # 递增数字
                        new_num = int(num_part) + 1
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
                        elif format_str == 'DEV0000':
                            # DeviceID格式：DEV0001, DEV0002...
                            return f"DEV{new_num:04d}"
            except Exception as e:
                print(f"查询最大ID失败: {e}")
        
        # 如果前缀不在已知列表中，或者查询失败，使用默认格式（确保长度不超过20位）
        timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")  # 12位时间戳
        random_num = str(hash(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")))[:2]  # 2位随机数
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
