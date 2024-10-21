# import os
# import boto3
# from flask import Flask, request, redirect, render_template, flash, url_for,session
# from config import Config
import boto3
from botocore.client import Config as BotoConfig
# app = Flask(__name__)
# app.config.from_object(Config)
# app.secret_key = os.urandom(24)
# users = {
#     "admin": "password123"  # 用户名: 密码
# }
#
# # 配置boto3客户端，连接Wasabi
# s3_client = boto3.client(
#     's3',
#     endpoint_url=app.config['WASABI_ENDPOINT_URL'],  # Wasabi的API endpoint
#     aws_access_key_id=app.config['WASABI_ACCESS_KEY'],  # Wasabi访问密钥
#     aws_secret_access_key=app.config['WASABI_SECRET_KEY']  ,# Wasabi私密密钥
#     config=BotoConfig(signature_version='s3v4')
# )
#
# # 文件上传路由
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         flash('没有选择文件')
#         return redirect(request.url)
#
#     file = request.files['file']
#     if file.filename == '':
#         flash('没有选择文件')
#         return redirect(request.url)
#
#     if file:
#         # 上传到Wasabi云存储
#         try:
#             s3_client.upload_fileobj(
#                 file,
#                 app.config['WASABI_BUCKET_NAME'],
#                 file.filename,
#                 ExtraArgs={'ACL': 'public-read'}  # 设置文件权限为公开读取
#             )
#             flash(f'文件 {file.filename} 上传成功！')
#         except Exception as e:
#             flash(f'文件上传失败：{str(e)}')
#
#     return redirect(url_for('index'))
# @app.route('/')
# def index():
#     if 'username' in session:
#         return f"欢迎回来，{session['username']}!"
#     return '欢迎来到云盘管理系统！请先登录。'
#
# # 处理用户退出登录的路由
# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     flash('您已退出登录。')
#     return redirect(url_for('login'))
#
# # 首页路由
# # @app.route('/')
# # def index():
# #     return render_template('index.html')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         # 验证用户名和密码
#         if username in users and users[username] == password:
#             session['username'] = username  # 登录成功，保存用户会话
#             flash('登录成功！')
#             return redirect(url_for('index'))
#         else:
#             flash('用户名或密码错误，请重试。')
#             return redirect(url_for('login'))
#
#     # 如果是 GET 请求，则显示登录页面
#     return render_template('login.html')
#
# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, request, redirect, render_template, flash, url_for, session
import os
import boto3
from botocore.client import Config as BotoConfig
from werkzeug.utils import secure_filename  # 确保文件名安全
from config import Config
app = Flask(__name__)
app.config.from_object(Config)  # 从配置文件加载配置
app.secret_key = os.urandom(24)

# 假设的用户数据库
users = {
    "admin": "wyq2004",  # 用户名: 密码
    "Wuyuqi": "1314520"
}
# 配置boto3客户端，连接Wasabi
s3_client = boto3.client(
    's3',
    endpoint_url=app.config['WASABI_ENDPOINT_URL'],  # Wasabi的API endpoint
    aws_access_key_id=app.config['WASABI_ACCESS_KEY'],  # Wasabi访问密钥
    aws_secret_access_key=app.config['WASABI_SECRET_KEY']  ,# Wasabi私密密钥
    config=BotoConfig(signature_version='s3v4')
)

# 登录页面和处理登录表单的路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 验证用户名和密码
        if username in users and users[username] == password:
            session['username'] = username  # 登录成功，保存会话信息
            flash('登录成功！')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误，请重试。')
            return redirect(url_for('login'))

    # 如果是 GET 请求，则显示登录页面
    return render_template('login.html')

# 主页路由
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])

    return redirect(url_for('login'))

# 用户登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('您已成功登出。')
    return redirect(url_for('login'))



# 文件上传路由
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('没有选择文件')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('没有选择文件')
        return redirect(request.url)

    if file:
        # 确保文件名安全
        filename = secure_filename(file.filename)
        # 上传到Wasabi云存储
        try:
            s3_client.upload_fileobj(
                file,
                app.config['WASABI_BUCKET_NAME'],
                filename,
                ExtraArgs={'ACL': 'public-read'}  # 设置文件权限为公开读取
            )
            flash(f'文件 {filename} 上传成功！')
        except Exception as e:
            flash(f'文件上传失败：{str(e)}')

    return redirect(url_for('index'))

@app.route('/files')
def list_files():
    try:
        response = s3_client.list_objects_v2(Bucket=app.config['WASABI_BUCKET_NAME'])
        files = [item['Key'] for item in response.get('Contents', [])]
        return render_template('files.html', files=files)
    except Exception as e:
        flash(f'无法获取文件列表：{str(e)}')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)