import mysql.connector
import os

def init_database():
    # 本地开发环境配置
    local_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'zx123456'
    }
    
    # 生产环境配置
    prod_config = {
        'host': '120.46.13.61',
        'user': 'root',
        'password': 'zhaoxiang123'
    }
    
    # 根据环境变量选择配置
    config = prod_config if os.getenv('ENV') == 'production' else local_config
    
    try:
        # 连接到MySQL服务器
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # 读取SQL文件
        with open('init_db.sql', 'r') as file:
            sql_commands = file.read()
        
        # 执行SQL命令
        for command in sql_commands.split(';'):
            if command.strip():
                cursor.execute(command)
        
        conn.commit()
        print("数据库初始化成功！")
        
    except mysql.connector.Error as err:
        print(f"数据库初始化失败: {err}")
    
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    init_database() 