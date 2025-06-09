import mysql.connector
from dotenv import load_dotenv
import os

# 加载环境变量
env = os.getenv('FLASK_ENV', 'development')
env_file = f'.env.{env}'
load_dotenv(env_file)

# 数据库连接配置
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'zx123456')
}

# 创建数据库连接
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# 创建数据库
db_name = os.getenv('DB_NAME', 'ai_boyfriend')
cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
cursor.execute(f"USE {db_name}")

# 创建用户表
cursor.execute("""
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nickname VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL,
    avatar_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")

# 创建聊天记录表
cursor.execute("""
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message_type VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    image_url VARCHAR(255),
    is_user_message BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
""")

# 提交更改并关闭连接
conn.commit()
cursor.close()
conn.close()

print("数据库初始化完成！") 