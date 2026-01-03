from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc

app = Flask(__name__)
app.secret_key = 'test_secret_key'

# 简化的数据库连接
conn_str = r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=.\SQLEXPRESS;DATABASE=SmartForestGrass;Trusted_Connection=yes'

@app.route('/')
def index():
    if 'user' in session:
        return f"欢迎 {session['user']['Name']}（{session['user']['Role']}）<br><a href='/logout'>退出登录</a>"
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    success = None
    
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            # 处理登录请求
            username = request.form['username']
            password = request.form['password']
            
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [User] WHERE Username = ?", (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user and user[2] == password and (user[6] == '启用' or user[6] == '1'):
                session['user'] = {
                    'UserID': user[0],
                    'Username': user[1],
                    'Name': user[3],
                    'Role': user[5],
                    'Status': user[6]
                }
                return redirect(url_for('index'))
            else:
                error = '用户名或密码错误'
    
    return render_template('login.html', error=error, success=success)

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        contact = request.form['contact']
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 检查用户名是否已存在
        cursor.execute("SELECT COUNT(*) FROM [User] WHERE Username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return render_template('login.html', error='用户名已存在')
        
        # 生成唯一的UserID
        cursor.execute("SELECT COUNT(*) FROM [User]")
        count = cursor.fetchone()[0]
        user_id = f"U{str(count + 1).zfill(3)}"
        
        # 插入新用户
        cursor.execute("INSERT INTO [User] (UserID, Username, Password, Name, Contact, Role, Status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      (user_id, username, password, name, contact, '公众用户', '启用'))
        conn.commit()
        conn.close()
        
        return render_template('login.html', success='注册成功，请登录')
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)