import boto3

from app.controllers import google_secret_controller


def get_secrets(secret_key_str, version_id=1):
    secret_controller = google_secret_controller.GoogleSecretController()
    return secret_controller.access_secret(secret_key_str, version_id)


class S3Controller:
    def __init__(self):
        self.AWS_ACCESS_KEY = get_secrets('AWS_ACCESS_KEY')
        self.AWS_SECRET_KEY = get_secrets('AWS_SECRET_KEY')
        self.BUCKET_NAME = get_secrets('S3_BUCKET_NAME')
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.AWS_ACCESS_KEY,
            aws_secret_access_key=self.AWS_SECRET_KEY
        )

    def put_object(self, object_name, file):
        self.s3.put_object(
            Bucket=self.BUCKET_NAME,
            Key=f'cert-img/{object_name}',
            Body=file,
            ContentType=file.content_type
        )

    def delete_object(self, object_name):
        self.s3.delete_object(Bucket=self.BUCKET_NAME, Key=f'cert-img/{object_name}')

    def get_image_url(self, object_name):
        location = self.s3.get_bucket_location(Bucket=self.BUCKET_NAME)['LocationConstraint']
        image_url = f'https://{self.BUCKET_NAME}.s3.{location}.amazonaws.com/cert-img/{object_name}'
        return image_url
