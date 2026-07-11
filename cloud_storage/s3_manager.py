import boto3
import os
from botocore.exceptions import ClientError

class S3CloudManager:
    def __init__(self):
        # क्लाउड क्रेडेंशियल्स (ये .env या सिक्योरिटी वॉल्ट से आएंगे)
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name='us-east-1'
        )
        self.bucket_name = "god-node-assets"

    def upload_asset(self, file_path: str, object_name: str = None) -> str:
        """AI द्वारा बनाए गए एसेट को क्लाउड पर अपलोड करना"""
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_name)
            # अपलोड के बाद पब्लिक लिंक देना
            return f"https://{self.bucket_name}.s3.amazonaws.com/{object_name}"
        except ClientError as e:
            print(f"[CLOUD ERROR]: Upload failed: {e}")
            return None

    def download_asset(self, object_name: str, download_path: str):
        """किसी भी डिवाइस से एसेट को वापस बुलाना"""
        try:
            self.s3_client.download_file(self.bucket_name, object_name, download_path)
            return True
        except ClientError as e:
            print(f"[CLOUD ERROR]: Download failed: {e}")
            return False

    def list_assets(self):
        """स्टोरेज में मौजूद सारे मॉडल्स की लिस्ट देखना"""
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        return [obj['Key'] for obj in response.get('Contents', [])]
                     
