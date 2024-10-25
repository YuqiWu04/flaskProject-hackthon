
from flask import Flask, request, redirect, render_template, flash, url_for, session, send_file, g
import os
import boto3
from botocore.client import Config as BotoConfig
from werkzeug.utils import secure_filename  # 确保文件名安全
from config import Config
import qrcode

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.urandom(24)


users = {
    "1111": "1111",
    "Wuyuqi": "1314520"
}

s3_client = boto3.client(
    's3',
    endpoint_url=app.config['WASABI_ENDPOINT_URL'],
    aws_access_key_id=app.config['WASABI_ACCESS_KEY'],
    aws_secret_access_key=app.config['WASABI_SECRET_KEY'],
    config=BotoConfig(signature_version='s3v4')
)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        if username in users and users[username] == password:
            session['username'] = username
            flash('Successfully logged in')
            return render_template('index.html', files=file_list())
        else:
            flash('Error!')
            return redirect(url_for('login'))


    return render_template('login.html')


# 主页路由
@app.route('/')
def index():
    g.isLogin = False
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    try:
        print(12333333)

        response = s3_client.list_objects_v2(Bucket=app.config['WASABI_BUCKET_NAME'])
        files = [obj['Key'] for obj in response.get('Contents', []) if 'Key' in obj]
    except Exception as e:
        flash(f"Error retrieving file list: {str(e)}")
        files = []


    print(files)

    return redirect(url_for('login'))



def file_list():
    try:
        print(12333333)

        response = s3_client.list_objects_v2(Bucket=app.config['WASABI_BUCKET_NAME'])
        files = [obj['Key'] for obj in response.get('Contents', []) if 'Key' in obj]
    except Exception as e:
        flash(f"Error retrieving file list: {str(e)}")
        files = []


    print(files)

    return files


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

        filename = secure_filename(file.filename)

        try:
            s3_client.upload_fileobj(
                file,
                app.config['WASABI_BUCKET_NAME'],
                filename,
                ExtraArgs={'ACL': 'public-read'}
            )
            flash(f'File {filename} upload successful')
        except Exception as e:
            flash(f'Fail: {str(e)}')

    return render_template('index.html', files=file_list())


from flask import send_from_directory


def download(file_name):
    try:
        s3_client.download_file("mybucket2025", file_name, f"/users/yukey/downloads/{file_name}")
        print(f"File {file_name} has been downloaded to /users/yukey/downloads")
    except Exception as e:
        print(f"Error downloading file: {e}")


@app.route('/download/<filename>')
def download_file(filename):
    local_directory = '/Users/yukey/downloads'
    download(filename)


    if os.path.exists(os.path.join(local_directory, filename)):
        try:

            return send_from_directory(local_directory, filename, as_attachment=True)
        except Exception as e:
            flash(f"Error retrieving local file: {str(e)}")
            return render_template('index.html', files=file_list())


    flash("The requested file does not exist.")
    return render_template('index.html', files=file_list())  # 或者可以返回一个自定义的404页面




@app.route('/delete/<filename>')
def delete_file(filename):
    try:
        s3_client.delete_object(Bucket="mybucket2025", Key=filename)
        print(f"File '{filename}' has been deleted from bucket.")
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
    # return redirect(url_for('index'))
    return render_template('index.html', files=file_list())


@app.route('/generate_qr/<filename>')
def generate_qr(filename):

    qr_content = f'{filename}'


    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)


    img = qr.make_image(fill='black', back_color='white')


    qr_image_path = os.path.join('static', f'qr_{filename}.png')
    img.save(qr_image_path)


    return send_file(qr_image_path)


if __name__ == '__main__':
    app.run(debug=True)
