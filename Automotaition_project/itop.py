import json
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Itop:
    def __init__(self):
        self.path_to_json_folder = os.environ['ITOP_JSON_DIRECTORY']
        self.php_version = os.environ['ITOP_PHP_VERSION']
        self.itop_login = os.environ['ITOP_LOGIN']
        self.itop_pwd = os.environ['ITOP_PASSWORD']
        self.language = "RU RU"
        self.pwd_for_user = "12345Qwerty!"
        self.profile_list = [{"profileid": 2}]

    def create_person(self, l_name, f_name, email, mob_phone, org_id, tab_nom=None, position=None):
        person_create_url = "https://itop.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s" \
                            "&json_data={\"operation\": \"core/create\", \"comment\": \"Adding new user\", \"class\": " \
                            "\"Person\", \"output_fields\": \"friendlyname, email\",\"fields\": {\"name\": \"%s\", " \
                            "\"first_name\": \"%s\", \"email\": \"%s\", \"mobile_phone\": \"%s\", " \
                            "\"employee_number\": \"%s\", \"function\": \"%s\",\"org_id\": \"%s\"}}" % \
                            (self.php_version, self.itop_login, self.itop_pwd, l_name, f_name, email, mob_phone,
                             tab_nom, position, org_id)
        person_id = \
            requests.request("POST", person_create_url, auth=HTTPBasicAuth(self.itop_login, self.itop_pwd)).json()[
                "objects"]
        print(person_id)

        for i in person_id:
            person_id = person_id[i]["key"]
            return person_id

    def create_login(self, fio, profile_list):
        ext_usr_create_url = "https://itop.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s" \
                             "&json_data={\"operation\": \"core/create\",\"comment\": \"Adding new user\", " \
                             "\"class\": \"UserExternal\", \"output_fields\": \"login, email\",\"fields\":" \
                             "{\"login\": \"%s\", \"language\": \"RU\", \"profile_list\": %s}} " % \
                             (self.php_version, self.itop_login, self.itop_pwd, fio, json.dumps(profile_list))

        user_id = \
            requests.request("POST", ext_usr_create_url, auth=HTTPBasicAuth(self.itop_login, self.itop_pwd)).json()[
                "objects"]

        for i in user_id:
            user_id = user_id[i]["key"]
            return user_id

    def merge_person_login(self, user_id, person_id):
        put_together_url = "https://itop.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s" \
                           "&json_data={\"operation\": \"core/update\",\"comment\": " \
                           "\"Adding Persona to new user\", \"class\": \"UserExternal\", \"key\":\"%s\", " \
                           "\"output_fields\": \"login, email\", \"fields\": {\"contactid\": \"%s\"}} " % \
                           (self.php_version, self.itop_login, self.itop_pwd, user_id, person_id)

        result = requests.request("PUT", put_together_url, auth=HTTPBasicAuth(self.itop_login, self.itop_pwd)).json()
        return result

    def get_user_id(self, f_name, l_name):
        user_get_url = "https://itop.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s" \
                       "&json_data={\"operation\": \"core/get\", \"class\": \"UserExternal\", \"key\": " \
                       "\"SELECT UserExternal WHERE contactid_friendlyname = '%s %s' \"}" % \
                       (self.php_version, self.itop_login, self.itop_pass, f_name, l_name)

        # GET_BLOCKING_USER_ID
        user = requests.request("GET", user_get_url, auth=HTTPBasicAuth(self.itop_login, self.itop_pass)).json()[
            "objects"]

        for i in user:
            blocking_user_id = user[i]["key"]
            print(f'Itop user id is {blocking_user_id}')
            return blocking_user_id

    def block_user(self, blocking_user_id):
        user_block_url = "https://itop.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s&json_data={" \
                         "\"operation\": \"core/update\", \"comment\": \"Blocking user\", \"class\": \"UserExternal\", " \
                         "\"key\": %s, \"output_fields\": \"login, email\", \"fields\": {\"status\": \"disabled\"}}" % \
                         (self.php_version, self.itop_login, self.itop_pass, blocking_user_id)

        # PUT_REQUEST_FOR_BLOCKING_USER
        response = requests.request("PUT", user_block_url, auth=HTTPBasicAuth(self.itop_login, self.itop_pass)).json()[
            "objects"]

        return response
