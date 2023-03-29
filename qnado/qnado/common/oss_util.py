# import os
# import oss2

from minio import Minio
from qnado import settings
from qnado.common.decorators import retry


# class AliyunOss(object):

#     def __init__(self):
#         self.access_key_id = settings.OSS_CONFIG['ACCESS_KEY_ID']
#         self.access_key_secret = settings.OSS_CONFIG['ACCESS_KEY_SECRET']
#         self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
#         self.bucket_name = settings.OSS_CONFIG['BUCKET_NAME']
#         self.endpoint = settings.OSS_CONFIG['ENDPOINT']
#         self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)

#     @retry(retry_times=3, fixed_sleep=1)
#     def put_object_from_file(self, key, file_path):
#         """
#         :param name: 在阿里云Bucket中要保存的文件名
#         :param file: 本地图片的文件名
#         :return:
#         """
#         self.bucket.put_object_from_file(key, file_path)
#         return "https://{}.{}/{}".format(self.bucket_name, self.endpoint, key)

class MinioOss:
    def __init__(self) -> None:
        self.end_point = settings.OSS_CONFIG['END_POINT']
        self.access_key = settings.OSS_CONFIG['ACCESS_KEY']
        self.secret_key = settings.OSS_CONFIG['SECRET_KEY']
        self.secure = settings.OSS_CONFIG['SECURE']
        self.bucket = settings.OSS_CONFIG['BUCKET']
        self.client = Minio(
            self.end_point,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

    @retry(retry_times=3, fixed_sleep=1)
    def put_object_from_file(self, key, file_path):
        self.client.fput_object(self.bucket, key, file_path)
        protocol = 'https' if self.secure else 'http'
        return f'{protocol}://{self.end_point}/{self.bucket}/{key}'

# oss = AliyunOss()
oss = MinioOss()
