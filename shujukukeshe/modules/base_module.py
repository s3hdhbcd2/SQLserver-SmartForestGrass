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
        生成唯一ID
        :param prefix: ID前缀
        :return: 唯一ID字符串
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_num = str(hash(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")))[:4]
        return f"{prefix}{timestamp}{random_num}"
    
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
