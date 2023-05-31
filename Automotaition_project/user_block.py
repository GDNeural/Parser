from dotenv import load_dotenv
import json
import os
import requests
from requests.auth import HTTPBasicAuth
from keycloak import Keycloak
import transliterate

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# API_CONNECT_CREDENTIALS
php_version = os.environ['ITOP_PHP_VERSION']
itop_login = os.environ['ITOP_LOGIN']
itop_pass = os.environ['ITOP_PASSWORD']


def user_block(path_to_file):
    with open(path_to_file, "r", encoding='utf-8') as file:
        user_info = json.load(file)["fields"]

        # GETTING_TAGS_FROM_USER_INFO
        f_name = user_info["first_name"]
        l_name = user_info["last_name"]
        mid_name = user_info["middle_name"]
        fio = transliterate.transliterate(str.lower(l_name + f_name[0] + mid_name[0]))

        # FORM_URL_FOR_USER_ID_INFO

        user_get_url = "https://itop.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s" \
                       "&json_data={\"operation\": \"core/get\", \"class\": \"UserExternal\", \"key\": " \
                       "\"SELECT UserExternal WHERE contactid_friendlyname = '%s %s' \"}" % \
                       (php_version, itop_login, itop_pass, f_name, l_name)
        blocking_user_id = ""

        # GET_BLOCKING_USER_ID
        user_for_blocking = requests.request("GET", user_get_url, auth=HTTPBasicAuth(itop_login, itop_pass)).json()[
            "objects"]

        for i in user_for_blocking:
            blocking_user_id = user_for_blocking[i]["key"]
            print(f'Itop user id is {blocking_user_id}')

        user_block_url = "https://itop.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s&json_data={" \
                         "\"operation\": \"core/update\", \"comment\": \"Blocking user\", \"class\": \"UserExternal\", " \
                         "\"key\": %s, \"output_fields\": \"login, email\", \"fields\": {\"status\": \"disabled\"}}" % \
                         (php_version, itop_login, itop_pass, blocking_user_id)

        # PUT_REQUEST_FOR_BLOCKING_USER
        blocked_user = requests.request("PUT", user_block_url, auth=HTTPBasicAuth(itop_login, itop_pass)).json()[
            "objects"]

        for i in blocked_user:
            print(f'User {fio} has been {blocked_user[i]["message"]}')

        keycloak = Keycloak()
        acc = keycloak.get_access_token()
        new_user_id = keycloak.get_user_id(fio, acc)['id']
        print(f'Keycloak user id is {new_user_id}')
        block_user = keycloak.block_user(new_user_id, acc)
        if block_user.status_code == 204:
            print(f'User {new_user_id} has been blocked successfully')

        # os.popen(f'rm -r --interactive=never -- "{path_to_file}"')
        print("Файл удален.")
