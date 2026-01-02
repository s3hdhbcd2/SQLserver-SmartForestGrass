from smart_forest_grass_business import DatabaseConnection

# 创建数据库连接实例
db_conn = DatabaseConnection()

# 连接数据库
if db_conn.connect():
    try:
        # 1. 查看当前有多少护林员用户
        rangers = db_conn.fetch_all("SELECT * FROM [User] WHERE Role = '区域护林员'")
        current_ranger_count = len(rangers)
        print(f"当前有 {current_ranger_count} 个区域护林员用户")
        
        # 2. 查看当前有多少个区域
        regions = db_conn.fetch_all("SELECT * FROM Region")
        region_count = len(regions)
        print(f"当前有 {region_count} 个区域")
        
        # 3. 创建更多的区域护林员用户（如果需要）
        rangers_needed = region_count - current_ranger_count
        if rangers_needed > 0:
            print(f"需要创建 {rangers_needed} 个新的区域护林员用户")
            
            # 生成新的护林员用户ID
            user_id_prefix = "U"
            last_user = db_conn.fetch_one("SELECT MAX(UserID) FROM [User]")
            if last_user and last_user[0]:
                last_user_id = int(last_user[0][1:])
            else:
                last_user_id = 25  # 从之前的检查结果来看，最后一个用户ID是U025
            
            new_rangers = []
            for i in range(rangers_needed):
                last_user_id += 1
                user_id = f"{user_id_prefix}{str(last_user_id).zfill(3)}"
                username = f"ranger{current_ranger_count + i + 1}"
                name = f"区域护林员{current_ranger_count + i + 1}"
                contact = f"ranger{current_ranger_count + i + 1}@example.com"
                
                # 检查用户名是否已存在
                check_sql = "SELECT COUNT(*) FROM [User] WHERE Username = ?"
                result = db_conn.fetch_one(check_sql, (username,))
                if result and result[0] == 0:
                    # 插入新的护林员用户
                    insert_sql = "INSERT INTO [User] (UserID, Username, Password, Name, Contact, Role, Status) VALUES (?, ?, ?, ?, ?, ?, ?)"
                    if db_conn.execute(insert_sql, (user_id, username, "123456", name, contact, "区域护林员", "启用")):
                        print(f"✅ 创建新护林员：{username} (UserID: {user_id})")
                        new_rangers.append((user_id, username, name))
                    else:
                        print(f"❌ 创建护林员失败：{username}")
                else:
                    print(f"⚠️  用户名已存在：{username}")
        
        # 4. 查看所有护林员用户（包括新创建的）
        rangers = db_conn.fetch_all("SELECT UserID, Username, Name FROM [User] WHERE Role = '区域护林员'")
        print(f"\n=== 所有护林员用户 ===")
        for ranger in rangers:
            print(f"UserID: {ranger[0]}, Username: {ranger[1]}, Name: {ranger[2]}")
        
        # 5. 为每个没有专门负责人的区域分配一个区域护林员
        print(f"\n=== 分配区域负责人 ===")
        # 获取所有区域护林员的UserID列表
        ranger_ids = [ranger[0] for ranger in rangers]
        ranger_index = 0
        
        for region in regions:
            region_id = region[0]
            region_name = region[1]
            current_manager = region[5]
            
            # 如果当前负责人是管理员(U001)，则分配一个区域护林员
            if current_manager == "U001":
                if ranger_index < len(ranger_ids):
                    new_manager_id = ranger_ids[ranger_index]
                    # 更新区域的负责人
                    update_sql = "UPDATE Region SET ManagerID = ? WHERE RegionID = ?"
                    if db_conn.execute(update_sql, (new_manager_id, region_id)):
                        print(f"✅ 区域 {region_name} (ID: {region_id}) 的负责人已更新为护林员 {new_manager_id}")
                    else:
                        print(f"❌ 更新区域 {region_name} 的负责人失败")
                    ranger_index += 1
                else:
                    print(f"⚠️  没有足够的护林员来分配给区域 {region_name}")
            else:
                print(f"⚠️  区域 {region_name} 已有专门的负责人 {current_manager}")
        
        # 6. 验证分配结果
        print(f"\n=== 分配结果验证 ===")
        region_managers = db_conn.fetch_all('SELECT r.RegionID, r.RegionName, u.UserID, u.Username, u.Name, u.Role FROM Region r LEFT JOIN [User] u ON r.ManagerID = u.UserID')
        for rm in region_managers:
            print(f"RegionID: {rm[0]}, RegionName: {rm[1]}, ManagerID: {rm[2]}, ManagerName: {rm[4]}, ManagerRole: {rm[5]}")
            
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
    finally:
        # 断开数据库连接
        db_conn.disconnect()
else:
    print('无法连接到数据库')
