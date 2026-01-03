from smart_forest_grass_business import DatabaseConnection

db_conn = DatabaseConnection()
db_conn.connect()

# 简化的用户数据插入
users = [
    ('U001', 'admin', '123456', '管理员', 'admin@example.com', '管理员', '启用'),
    ('U002', 'data_admin', '123456', '数据管理员', 'data@example.com', '数据管理员', '启用'),
    ('U003', 'ranger1', '123456', '区域护林员1', 'ranger1@example.com', '区域护林员', '启用'),
    ('U004', 'public1', '123456', '公众用户1', 'public1@example.com', '公众用户', '启用'),
    ('U005', 'supervisor1', '123456', '监管人员1', 'supervisor1@example.com', '监管人员', '启用')
]

# 插入区域数据
regions = [
    ('R001', '华北林区', '森林', 116.4074, 39.9042, 'U001'),
    ('R002', '东北林区', '森林', 126.6318, 45.7569, 'U001')
]

print('正在插入测试用户数据...')

# 先删除现有用户数据
db_conn.execute("DELETE FROM [User]")

# 插入用户数据
for user in users:
    sql = "INSERT INTO [User] (UserID, Username, Password, Name, Contact, Role, Status) VALUES (?, ?, ?, ?, ?, ?, ?)"
    result = db_conn.execute(sql, user)
    if result:
        print(f"✅ 插入用户 {user[1]} 成功")
    else:
        print(f"❌ 插入用户 {user[1]} 失败")

# 插入区域数据
db_conn.execute("DELETE FROM Region")
for region in regions:
    sql = "INSERT INTO Region (RegionID, RegionName, RegionType, Longitude, Latitude, ManagerID, CreateTime) VALUES (?, ?, ?, ?, ?, ?, GETDATE())"
    result = db_conn.execute(sql, region)
    if result:
        print(f"✅ 插入区域 {region[1]} 成功")
    else:
        print(f"❌ 插入区域 {region[1]} 失败")

print('测试数据插入完成！')
db_conn.disconnect()
