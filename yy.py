import qrcode
import os
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

generate_qr('111')