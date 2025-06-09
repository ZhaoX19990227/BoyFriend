-- 创建数据库
CREATE DATABASE IF NOT EXISTS ai_boyfriend;
USE ai_boyfriend;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nickname VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('1', '0', '0.5', 'side') NOT NULL,
    avatar_url VARCHAR(255) DEFAULT 'http://120.46.13.61/images/1.jpeg',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建聊天记录表
CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message_type ENUM('text', 'image') NOT NULL,
    content TEXT NOT NULL,
    image_url VARCHAR(255),
    is_user_message BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建索引
CREATE INDEX idx_user_id ON chat_messages(user_id);
CREATE INDEX idx_created_at ON chat_messages(created_at); 