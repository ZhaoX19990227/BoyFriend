# AI男友聊天网站

这是一个基于Flask的AI男友聊天网站，支持用户注册、登录和与AI男友进行文字和图片对话。

## 功能特点

- 用户注册和登录系统
- 支持文字和图片对话
- 聊天记录持久化存储
- 美观的粉色系UI设计
- 基于KIMI LLM的智能对话

## 环境要求

- Python 3.8+
- MySQL 5.7+
- 其他依赖见requirements.txt

## 安装步骤

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 初始化数据库：
   ```bash
   python init_database.py
   ```
4. 配置环境变量：
   - 创建.env文件
   - 设置必要的环境变量（见.env.example）

## 运行项目

```bash
python app.py
```

## 项目结构

```
.
├── app.py              # 主应用文件
├── init_db.sql         # 数据库初始化脚本
├── init_database.py    # 数据库初始化程序
├── requirements.txt    # 项目依赖
├── static/            # 静态文件
├── templates/         # HTML模板
└── uploads/          # 上传文件目录
```

## 注意事项

- 请确保MySQL服务已启动
- 生产环境部署时请修改相应的数据库配置
- 请妥善保管API密钥