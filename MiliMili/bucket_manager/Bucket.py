import platform

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
import os


class Bucket:
    base_path = os.path.dirname(os.path.dirname(__file__))
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    proxies = {
        'http': '127.0.0.1:80',
        'https': '127.0.0.1:443'
    }

    def __init__(self, secret_id='AKIDNZVAYfV5NO9dqmTv5zcz4sPggPr2yc07', secret_key='sTnqc7LJ0Q2NREl10h8IBn8CyTigNo31',
                 app_id='-1309504341', region='ap-beijing', token=None):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.app_id = app_id
        self.region = region
        self.token = token
        self.config = CosConfig(Region=self.region, Secret_id=self.secret_id, Secret_key=self.secret_key,
                                Token=self.token)
        self.client = CosS3Client(self.config)

    def create_bucket(self, bucket_name, access='public-read'):
        """
        :param access: access status: public-read | private | public-read-write
        :param bucket_name: bucket's name
        :return: -1:create unsuccessfully, 0 bucket already exists, 1 create successfully
        """
        if not self.client.bucket_exists(Bucket=bucket_name + self.app_id):
            try:
                self.client.create_bucket(Bucket=bucket_name + self.app_id, ACL=access)
            except Exception:
                return -1
            else:
                return 1
        return 0

    def upload_file(self, bucket_name, key_name, file_name):
        """
        :param bucket_name: bucket's name
        :param key_name: key's name in bucket
        :param file_name: file's name in /media
        :return: -1:create or update unsuccessfully, 1 create or update successfully
        """
        try:
            if platform.system() == "Linux":
                self.client.upload_file(
                    Bucket=bucket_name + self.app_id,
                    LocalFilePath=self.base_path + '\\media\\' + file_name,
                    Key=key_name,
                    PartSize=1,
                    MAXThread=10,
                )
            else:
                self.client.upload_file(
                    Bucket=bucket_name + self.app_id,
                    LocalFilePath=self.base_path + '/media/' + file_name,
                    Key=key_name,
                    PartSize=1,
                    MAXThread=10,
                )
        except Exception:
            return -1
        else:
            return 1

    def delete_object(self, bucket_name, key_name):
        """
        :param bucket_name: bucket's name
        :param key_name: key's name in bucket
        :return: delete unsuccessfully, 1 delete successfully
        """
        try:
            self.client.delete_object(
                Bucket=bucket_name + self.app_id,
                Key=key_name
            )
        except Exception:
            return -1
        else:
            return 1

    def query_object(self, bucket_name, key_name):
        """
        :param bucket_name: bucket's name
        :param key_name: key's name in bucket
        :return: None(NoneType) query unsuccessfully, url(str) query successfully
        """
        if self.client.bucket_exists(Bucket=bucket_name + self.app_id) and \
                self.client.object_exists(Bucket=bucket_name + self.app_id, Key=key_name):
            try:
                return self.client.get_object_url(
                    Bucket=bucket_name + self.app_id,
                    Key=key_name
                )
            except Exception:
                return None
        return None