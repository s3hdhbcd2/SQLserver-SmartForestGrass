import pyodbc

# Connect to the database
conn = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=.\\SQLEXPRESS;DATABASE=SmartForestGrass;Trusted_Connection=yes')
cursor = conn.cursor()

print('已创建的表：')
cursor.execute("SELECT name FROM sys.tables WHERE type = 'U' ORDER BY name")
tables = cursor.fetchall()
for table in tables:
    print(f'- {table[0]}')

print('\n主要表数据统计：')
# Check some key tables
key_tables = ['User', 'Region', 'Sensor', 'MonitoringData', 'WarningRule', 'WarningRecord', 'DeviceArchive', 'ForestResource']
for table in key_tables:
    if table == 'User':
        cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
    else:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f'{table}: {count}行')

conn.close()