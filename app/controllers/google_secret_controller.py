from google.cloud import secretmanager
import os

PROJECT_ID = '595401715712'
CREDENTIAL_PATH = '/Users/eunbin/Dev/happy-birthdonay-backend/planar-alliance-421215-18a00d489f97.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIAL_PATH

class GoogleSecretController:
    def __init__(self):
        self.project_id = PROJECT_ID

    def access_secret(self, secret_id, version_id=1):
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode('UTF-8')
