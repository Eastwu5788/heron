import datetime
import os
import time
import hashlib
from flask import request

from PIL import Image, ImageFilter
from app import db
from app.helper.secret import md5
from app.models.social.image import ImageModel


def generate_image_file():
    """
    生成图片文件存储路径
    """
    from heron import app

    today = datetime.datetime.today()
    path = "upload/%d/%02d/%02d/" % (today.year, today.month, today.day)
    full_path = os.path.join(app.config["UPLOAD_IMG_PATH"], path)
    if not os.path.exists(full_path):
        os.makedirs(full_path, 0o777)
    return path


def hash_file(file):
    if not file:
        return None

    md5obj = hashlib.md5()
    md5obj.update(file.read())
    return md5obj.hexdigest()


class UploadImage(object):

    image_size = ['o', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'x']

    def __init__(self):
        self.images = self.pre_upload()

    def pre_upload(self):
        image_info_list = []

        image = request.files.get("image")
        if image:
            image_info_list.append(UploadImage.format_image(image))

        for item in request.files.getlist("image[]"):
            image_info_list.append(UploadImage.format_image(item))

        return image_info_list

    def save_images(self):

        for img_dic in self.images:
            if not img_dic:
                continue
            self.save_image(img_info=img_dic)

        # 提交事务
        db.session.commit()

    def save_image(self, img_info):

        image = ImageModel()
        image.image_width = img_info["width"]
        image.image_height = img_info["height"]
        image.hash_key = img_info["hash_key"]
        image.file_name = generate_image_file()
        image.file_ext = "jpg"
        image.mime_type = img_info["mime_type"]
        image.file_size = img_info["file_size"]
        image.status = 1

        pil_img = img_info["pil_image"]
        if image.mime_type in ("RGBA", "LA"):
            background = Image.new(pil_img.mode[:-1], pil_img.size, "#ffffff")
            background.paste(pil_img, pil_img.split()[-1])
            pil_img = background

        from heron import app
        prefix_path = app.config["UPLOAD_IMG_PATH"]
        for size in self.image_size:
            abs_path = UploadImage.generate_image_file_path(image.hash_key, size)
            img = pil_img.copy()
            full_path = os.path.join(prefix_path, abs_path)
            # 原图
            if size == 'o':
                image.image_o = abs_path
                img.save(full_path, "jpeg", quality=90)

            # 小头像 100*100
            elif size == 'a':
                image.image_a = abs_path
                img.thumbnail((100, 100))
                img.save(full_path, "jpeg", quality=90)
            # 大头像 240*240
            elif size == 'b':
                image.image_b = abs_path
                img.thumbnail((240, 240))
                img.save(full_path, "jpeg", quality=90)
            # 小方图
            elif size == 'c':
                image.image_c = abs_path
                img.thumbnail((400, 400))
                img.save(full_path, "jpeg", quality=90)
            # 大方图
            elif size == 'd':
                image.image_d = abs_path
                img.thumbnail((800, 800))
                img.save(full_path, "jpeg", quality=90)
            # 等比缩放 最大高度600
            elif size == 'e':
                image.image_e = abs_path
                img.thumbnail((600, 600))
                img.save(full_path, "jpeg", quality=90)
            # 等比例缩放 最大宽高800
            elif size == 'f':
                image.image_f = abs_path
                img.thumbnail((800, 800))
                img.save(full_path, "jpeg", quality=90)
            # 等比缩放 最大宽高1000
            elif size == 'g':
                image.image_g = abs_path
                img.thumbnail((1000, 1000))
                # TODO: 添加水印
                img.save(full_path, "jpeg", quality=90)
            elif size == 'x':
                image.image_x = abs_path
                img = img.filter(ImageFilter.BLUR)
                img = img.filter(ImageFilter.GaussianBlur(radius=4))
                img = img.filter(ImageFilter.MedianFilter)
                img.save(full_path, "jpeg")

        # 添加对象到数据库session中
        db.session.add(image)
        img_info["image"] = image

    @staticmethod
    def format_image(image):
        result = dict()
        result["ori_image"] = image
        result["hash_key"] = hash_file(image)

        pil_image = Image.open(image)
        result["pil_image"] = pil_image
        result["width"] = pil_image.width
        result["height"] = pil_image.height
        result["mime_type"] = pil_image.mode
        result["file_size"] = len(image.read())

        return result

    @staticmethod
    def generate_image_file_path(hash_key, size='o'):
        """
        生成图片的唯一路径
        """
        ori_key = hash_key + "_" + size + str(time.time())
        img_name = md5(ori_key) + ".jpg"
        return os.path.join(generate_image_file(), img_name)