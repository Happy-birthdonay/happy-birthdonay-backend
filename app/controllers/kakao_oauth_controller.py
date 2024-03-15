import requests

from kakao_config import KAKAO_REST_API_KEY, KAKAO_REDIRECT_URI, KAKAO_CLIENT_SECRET


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
        params = {
            'grant_type': 'authorization_code',
            'client_id': KAKAO_REST_API_KEY,
            'client_secret': KAKAO_CLIENT_SECRET,
            'redirect_uri': KAKAO_REDIRECT_URI,
            'code': code
        }

        return requests.post(url, headers=self.default_headers, params=params)

    def get_user_info(self, access_token):
        url = self.api_server % '/v2/user/me'
        headers = {
            **self.default_headers,
            **{'Authorization': f'Bearer {access_token}'}
        }
        params = {
            'property_keys': ["kakao_account.name", "kakao_account.birthday"]
        }

        return requests.post(url, headers=headers, params=params)
