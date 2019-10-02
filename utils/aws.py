from botocore.client import Config
from django.conf import settings
import boto3
import io

class S3Client:

    def __init__(self, bucket):
        self.client = self.s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                            region_name='ca-central-1',
                            config=Config(signature_version='s3v4'))
        self.bucket = bucket

    def upload_image(self, fileobj, filename):
        self.client.upload_fileobj(fileobj, self.bucket, filename, ExtraArgs={'ContentType': 'image/jpeg', 'ACL': 'public-read'})

    def upload_object(self, fileobj, filename, content_type):
        self.client.upload_fileobj(fileobj, self.bucket, filename, ExtraArgs={'ContentType': content_type})

    def delete_object(self, key):
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def download_object(self, key):
        fileobj = io.BytesIO()
        self.client.download_fileobj(self.bucket, key, fileobj)
        fileobj.seek(0)
        return fileobj

    def get_presigned_url(self, key, expiry=3600):
        return self.client.generate_presigned_url(ClientMethod='get_object', Params={'Key': key, 'Bucket': self.bucket}, ExpiresIn=expiry)