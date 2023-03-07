import json

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from requests import packages

from ...settings import settings

packages.urllib3.disable_warnings(packages.urllib3.exceptions.InsecureRequestWarning)

oauth2_scheme_crm = OAuth2PasswordBearer(tokenUrl="crm/v1/keycloak/login")
oauth2_scheme_lk = OAuth2PasswordBearer(tokenUrl="lk/v1/keycloak/login")


class KeycloakLK:
    kc_path = settings.kc_hostname
    realm = settings.kc_realm_name

    def __init__(self) -> None:
        self.logout_endpoint = f"{KeycloakLK.kc_path}/realms/{KeycloakLK.realm}/protocol/openid-connect/logout"
        self.token_endpoint = f"{KeycloakLK.kc_path}/realms/{KeycloakLK.realm}/protocol/openid-connect/token"
        self.user_info_endpoint = f"{KeycloakLK.kc_path}/realms/{KeycloakLK.realm}/protocol/openid-connect/userinfo"
        self.client_id = settings.kc_client_id
        self.client_secret = settings.kc_client_secret_key

    def is_crm(self, response, crm):
        user = self.get_user_info(response.json()["access_token"])
        if crm:
            if "group" in user and user["group"] and len(user["group"]) > 0:
                return response.json()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Conflict")
        else:
            if "group" in user and user["group"] and len(user["group"]) > 0:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Conflict")
            return response.json()

    def get_access_token(self, username, password, crm):
        payload = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.request("POST", self.token_endpoint, data=payload, verify=False)
        if response.status_code == 401:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Conflict")
        return self.is_crm(response, crm)

    def refresh_session_by_refresh_token(self, ref_token, crm):
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": ref_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.request("POST", self.token_endpoint, data=payload, verify=False)
        return self.is_crm(response, crm)
    
    def logout(self, refresh_token):
        payload = {
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.request("POST", self.logout_endpoint, data=payload, verify=False)
        if response.status_code == 204:
            return
        raise HTTPException(status_code=response.status_code, detail=response.json())

    def get_access_token_by_auth_code(self, auth_code):
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.request("POST", self.token_endpoint, data=payload, verify=False)
        return response.json()

    def get_user_info(self, token):
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("POST", self.user_info_endpoint, headers=headers, verify=False)
        if response.status_code == 401:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=response.json())
        return response.json()


class KeycloakAdmin:
    kc_path = settings.kc_hostname
    realm = settings.kc_realm_name
    
    def __init__(self) -> None:
        self.users_endpoint = f"{KeycloakAdmin.kc_path}/admin/realms/{KeycloakAdmin.realm}/users"
        self.token_endpoint = f"{KeycloakAdmin.kc_path}/realms/master/protocol/openid-connect/token"
        self.client_id = "admin-cli"
        self.username = settings.kc_admin
        self.password = settings.kc_admin_password
        self._access_token = None

    @property
    def access_token(self):
        if self._access_token is None:
            payload = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": self.client_id
            }
            response = requests.request("POST", self.token_endpoint, data=payload, verify=False)
            self._access_token = response.json()["access_token"]
        return self._access_token

    def create_user(self, email, phone, password=None):
        payload = {
            "firstName": "test",
            "lastName": "test",
            "email": email,
            "enabled": "true",
            "username": phone,
            "attributes": {"custom_attr": "test"},
        }
        if password:
            payload["credentials"] = [
                {"value": password, "type": "password"}
            ]
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.request("POST", self.users_endpoint, headers=headers, data=json.dumps(payload), verify=False)
        if response.status_code == 201:
            return response.headers['Location'].split('/')[-1]
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response.json())

    def update_user(self, user_id, email=None, phone=None):
        payload = {}
        if email is not None:
            payload["email"] = email
        if phone is not None:
            payload["username"] = phone

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        url = f"{self.users_endpoint}/{user_id}"
        response = requests.request("PUT", url, headers=headers, data=json.dumps(payload), verify=False)
        if response.status_code == 204:
            return
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response.json())

    def set_password(self, user_id, new_password, confirmation):
        if new_password != confirmation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "type": "password",
            "temporary": False,
            "value": new_password
        })
        url = f"{self.users_endpoint}/{user_id}/reset-password"
        response = requests.request("PUT", url, headers=headers, data=payload, verify=False)
        if response.status_code == 204:
            return
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response.text)

    def get_user(self, phone):
        url = f"{self.users_endpoint}?username={phone.replace('+', '')}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.request("GET", url, headers=headers, verify=False)
        profiles = response.json()
        if response.status_code == 200 and len(profiles) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return profiles[0]

    def get_roles(self, user_id):
        url = f"{self.users_endpoint}/{user_id}/role-mappings/realm"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.request("GET", url, headers=headers, verify=False)
        roles = response.json()
        if response.status_code == 200 and len(roles) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return roles

    def get_and_delete_users(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.request("GET", self.users_endpoint, headers=headers, verify=False)
        profiles = response.json()
        for p in profiles:
            response = requests.request("DELETE", f"{self.users_endpoint}/{p['id']}", headers=headers, verify=False)


async def get_user_crm(
        keycloak_lk: KeycloakLK = Depends(KeycloakLK),
        token: str = Depends(oauth2_scheme_lk)
):
    user = keycloak_lk.get_user_info(token)
    return user


async def get_user(
        keycloak_lk: KeycloakLK = Depends(KeycloakLK),
        token: str = Depends(oauth2_scheme_lk)
):
    user = keycloak_lk.get_user_info(token)
    return user
