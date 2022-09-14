import hashlib
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"


class PublicMediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = False

    # def _normalize_name(self, name):
    #  print(name)
    #  return super()._normalize_name(name)
    #  #return hashlib.md5(name.encode()).hexdigest()
