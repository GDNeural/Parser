import json
import os
import requests
from dotenv import load_dotenv
from requests import packages

packages.urllib3.disable_warnings(packages.urllib3.exceptions.InsecureRequestWarning)


class Keycloak:
    # Loading virtual environment
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    # Initiating all-used variables

    def __init__(self) -> None:
        self.kc_url_users = f"{os.environ['KC_URL']}/admin/realms/{os.environ['KC_REALM']}/users"
        self.kc_token_url = f"{os.environ['KC_URL']}/realms/master/protocol/openid-connect/token"
        self.kc_username = os.environ['KC_USERNAME']
        self.kc_pwd = os.environ['KC_PASSWORD']
        self.kc_client_id = os.environ['KC_CLIENT_ID']
        self.kc_secret = os.environ['KC_CLIENT_SECRET']

    def get_access_token(self):
        kc_token_data = {
            "username": self.kc_username,
            "password": self.kc_pwd,
            "client_id": self.kc_client_id,
            "client_secret": self.kc_secret,
            "grant_type": "password"
        }
        access_token = requests.request("POST", self.kc_token_url, data=kc_token_data).json()["access_token"]
        return access_token

    def register_user(self, fio, email, f_name, l_name, pwd_for_user, acc_token):
        usr_create_data = {
            "enabled": True,
            "username": fio,
            "email": email,
            "firstName": f_name,
            "lastName": l_name,
            "attributes": {"custom_attr": "test"},
            "credentials": [
                {
                    "type": "password",
                    "value": pwd_for_user,
                    "temporary": True
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {acc_token}",
            "Content-Type": "application/json"
        }
        kc_response = requests.request("POST", self.kc_url_users, headers=headers, data=json.dumps(usr_create_data))
        return kc_response

    def get_user_id(self, username, access_token):
        url = f"{self.kc_url_users}?username={username}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.request("GET", url, headers=headers, verify=False).json()[0]
        return response

    def block_user(self, user_id, access_token):
        url = f"{self.kc_url_users}/{user_id}"
        usr_create_data = {
            "enabled": False,
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.request("PUT", url, headers=headers, data=json.dumps(usr_create_data), verify=False)
        return response
