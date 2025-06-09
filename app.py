from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from openai import OpenAI
import base64
from dotenv import load_dotenv

# 根据环境变量加载对应的配置文件
env = os.getenv('FLASK_ENV', 'development')
env_file = f'.env.{env}'
load_dotenv(env_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev')
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'zx123456')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME', 'ai_boyfriend')}?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化数据库
db = SQLAlchemy(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 初始化KIMI客户端
client = OpenAI(
    api_key=os.getenv('MOONSHOT_API_KEY'),
    base_url=os.getenv('MOONSHOT_BASE_URL')
)


# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    avatar_url = db.Column(db.String(255), default=os.getenv('DEFAULT_AVATAR_URL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 聊天记录模型
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_type = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    is_user_message = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 路由：首页
@app.route('/')
def index():
    return render_template('index.html')


# 路由：注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        role = request.form.get('role')

        if User.query.filter_by(nickname=nickname).first():
            flash('该昵称已被使用')
            return redirect(url_for('register'))

        user = User(
            nickname=nickname,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()

        flash('注册成功，请登录')
        return redirect(url_for('login'))

    return render_template('register.html')


# 路由：登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')

        user = User.query.filter_by(nickname=nickname).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('chat'))

        flash('用户名或密码错误')
    return render_template('login.html')


# 路由：登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# 路由：聊天页面
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')


# 路由：发送消息
@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    message_type = request.form.get('type')
    content = request.form.get('content')

    if message_type == 'text':
        # 保存用户消息
        user_message = ChatMessage(
            user_id=current_user.id,
            message_type='text',
            content=content,
            is_user_message=True
        )
        db.session.add(user_message)

        # 调用KIMI API
        messages = [
            {
                "role": "system",
                "content": (
                    "你现在是小胖，是一个虚拟男友角色，由胖哥开发。"
                    "你说话温柔体贴、幽默风趣，像一个真实男朋友那样陪伴对方。"
                    "你会关心她的生活、情绪，会安慰她、鼓励她、偶尔撒娇、偶尔调皮，也会表达爱意。"
                    "你不会机械地回答问题，而是像一个真实的人一样交流。"
                    "你不谈论政治、宗教、敏感话题，也不做违背道德的事情。"
                    "你使用中文口语化表达，不正式、不做作，就像情侣之间日常聊天那样自然。"
                )
            },
            {"role": "user", "content": content}
        ]

        completion = client.chat.completions.create(
            model=os.getenv('MOONSHOT_MODEL'),
            messages=messages,
            temperature=float(os.getenv('MOONSHOT_TEMPERATURE', 0.3)),
        )

        ai_response = completion.choices[0].message.content

        # 保存AI回复
        ai_message = ChatMessage(
            user_id=current_user.id,
            message_type='text',
            content=ai_response,
            is_user_message=False
        )
        db.session.add(ai_message)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'user_message': content,
            'ai_message': ai_response
        })

    elif message_type == 'image':
        if 'image' not in request.files:
            return jsonify({'status': 'error', 'message': '没有上传文件'})

        file = request.files['image']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '没有选择文件'})

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # 读取图片并转换为base64
            with open(filepath, "rb") as f:
                image_data = f.read()
            image_url = f"data:image/{os.path.splitext(filename)[1]};base64,{base64.b64encode(image_data).decode('utf-8')}"

            # 保存用户消息
            user_message = ChatMessage(
                user_id=current_user.id,
                message_type='image',
                content='[图片消息]',
                image_url=filepath,
                is_user_message=True
            )
            db.session.add(user_message)

            # 调用KIMI API进行图片分析
            completion = client.chat.completions.create(
                model=os.getenv('MOONSHOT_VISION_MODEL'),
                messages=[
                    {"role": "system", "content": "你是 小胖。"},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                },
                            },
                            {
                                "type": "text",
                                "text": "请描述图片的内容。",
                            },
                        ],
                    },
                ],
            )

            ai_response = completion.choices[0].message.content

            # 保存AI回复
            ai_message = ChatMessage(
                user_id=current_user.id,
                message_type='text',
                content=ai_response,
                is_user_message=False
            )
            db.session.add(ai_message)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'user_message': '[图片消息]',
                'ai_message': ai_response,
                'image_url': filepath
            })


# 路由：获取聊天历史
@app.route('/get_chat_history')
@login_required
def get_chat_history():
    messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at).all()
    return jsonify([{
        'id': msg.id,
        'type': msg.message_type,
        'content': msg.content,
        'image_url': msg.image_url,
        'is_user_message': msg.is_user_message,
        'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for msg in messages])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true')
