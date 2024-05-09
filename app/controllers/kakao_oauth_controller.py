import requests

from app.controllers import google_secret_controller


def get_secrets(secret_key_str):
    secret_controller = google_secret_controller.GoogleSecretController()
    return secret_controller.access_secret(secret_key_str)


class KakaoOAuthController:
    def __init__(self):
        self.oauth_server = 'https://kauth.kakao.com%s'
        self.api_server = 'https://kapi.kakao.com%s'
        self.default_headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Cache-Control': 'no-cache'
        }

    def authorization(self, code):
        url = self.oauth_server % '/oauth/token'

        KAKAO_REST_API_KEY = get_secrets('kakao_rest_api_key')
        KAKAO_CLIENT_SECRET = get_secrets('kakao_client_secret')
        KAKAO_REDIRECT_URI = get_secrets('kakao_redirect_uri')

        params = {
            'grant_type': 'authorization_code',
            'client_id': KAKAO_REST_API_KEY,
            'client_secret': KAKAO_CLIENT_SECRET,
            'redirect_uri': KAKAO_REDIRECT_URI,
            'code': code
        }

        return requests.post(url, headers=self.default_headers, params=params).json()

    def get_user_info(self, access_token):
        url = self.api_server % '/v2/user/me'
        headers = {
            **self.default_headers,
            **{'Authorization': f'Bearer {access_token}'}
        }

        return requests.post(url, headers=headers).json()
