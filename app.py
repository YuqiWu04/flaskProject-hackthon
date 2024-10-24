# import os
# import boto3
# from flask import Flask, request, redirect, render_template, flash, url_for,session
# from config import Config
# import boto3
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
from flask import Flask, request, redirect, render_template, flash, url_for, session, send_file
import os
import boto3
from botocore.client import Config as BotoConfig
from werkzeug.utils import secure_filename  # 确保文件名安全
from config import Config
import qrcode

app = Flask(__name__)
app.config.from_object(Config)  # 从配置文件加载配置
app.secret_key = os.urandom(24)

# 假设的用户数据库
users = {
    "1111": "1111",  # 用户名: 密码
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
            flash('Successfully logged in')
            return redirect(url_for('index'))
        else:
            flash('Error!')
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
    flash('Successfully logged out')
    return redirect(url_for('login'))



# 文件上传路由
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Please select a file!')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('Please select a file!')
        return redirect(request.url)

    if file:
        # 确保文件名安全
        filename = secure_filename(file.filename)
        if file:
            # 确保文件名安全
            filename = secure_filename(file.filename)

            # 保存文件到指定目录
            directory = '/Users/yukey/Desktop/files backup'
            # 创建目录（如果不存在的话）
            os.makedirs(directory, exist_ok=True)

            # 保存文件
            file_path = os.path.join(directory, filename)
            file.save(file_path)  # 保存文件到指定路径

        # 上传到Wasabi云存储
        try:
            s3_client.upload_fileobj(
                file,
                app.config['WASABI_BUCKET_NAME'],
                filename,
                ExtraArgs={'ACL': 'public-read'}  # 设置文件权限为公开读取
            )
            flash(f'File {filename} upload successful')
        except Exception as e:
            flash(f'Fail: {str(e)}')

    return redirect(url_for('index'))


@app.route('/files')
def file_list():
    try:
        # 获取存储桶中的文件列表
        response = s3_client.list_objects_v2(Bucket=app.config['WASABI_BUCKET_NAME'])
        files = [obj['Key'] for obj in response.get('Contents', [])]  # 获取文件名
    except Exception as e:
        flash(f"Error retrieving file list: {str(e)}")
        files = []

    return render_template('files.html', files=files)

from flask import send_from_directory

@app.route('/download/<filename>')
def download_file(filename):
    directory = '/Users/yukey/Desktop/files backup'
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    directory = '/Users/yukey/Desktop/files backup'
    try:
        os.remove(os.path.join(directory, filename))
        flash(f"{filename} already delete")
    except Exception as e:
        flash(f"Error: {e}")
    return redirect(url_for('file_list'))

@app.route('/generate_qr/<filename>')
def generate_qr(filename):
    # 生成二维码的内容
    qr_content = f'https://s3.ap-southeast-1.wasabisys.com/{filename}'  # 确保这里的 URL 是正确的

    # 生成二维码图像
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    # 创建一个二维码图像
    img = qr.make_image(fill='black', back_color='white')

    # 保存二维码图像
    qr_image_path = os.path.join('static', f'qr_{filename}.png')
    img.save(qr_image_path)

    # 返回二维码图像的路径
    return send_file(qr_image_path)
if __name__ == '__main__':
    app.run(debug=True)
