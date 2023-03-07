from dotenv import load_dotenv
import json
import os
import requests
from requests.auth import HTTPBasicAuth

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# PATH_TO_USER_FILES
path_to_json_folder = os.environ['ITOP_JSON_DIRECTORY']
list_of_files = os.listdir(path_to_json_folder)

# API_CONNECT_CREDENTIALS
php_version = os.environ['ITOP_PHP_VERSION']
login = os.environ['ITOP_LOGIN']
password = os.environ['ITOP_PASSWORD']

for file in list_of_files:
    path_to_file = path_to_json_folder + file
    with open(path_to_file, "r", encoding='utf-8') as read_file:
        json_data = json.load(read_file)
        user_info = json_data["fields"]

        # GETTING_TAGS_FROM_USER_INFO
        first_name = user_info["first_name"]
        last_name = user_info["last_name"]

        # FORM_URL_FOR_USER_ID_INFO

        user_get_url = "https://itop.cunet.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s" \
                       "&json_data={\"operation\": \"core/get\", \"class\": \"UserLocal\", \"key\": " \
                       "\"SELECT UserLocal WHERE contactid_friendlyname = '%s %s' \"}" % \
                       (php_version, login, password, first_name, last_name)
        blocking_user_id = ""

        # GET_BLOCKING_USER_ID
        user_for_blocking = requests.request("GET", user_get_url, auth=HTTPBasicAuth(login, password)).json()["objects"]
        for i in user_for_blocking:
            blocking_user_id = user_for_blocking[i]["key"]
            print(blocking_user_id)

        user_block_url = "https://itop.cunet.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s&json_data={" \
                         "\"operation\": \"core/update\", \"comment\": \"Blocking user\", \"class\": \"UserLocal\", " \
                         "\"key\": %s, \"output_fields\": \"login, email\", \"fields\": {\"status\": \"disabled\"}}" % \
                         (php_version, login, password, blocking_user_id)

        # PUT_REQUEST_FOR_BLOCKING_USER
        blocked_user = requests.request("PUT", user_block_url, auth=HTTPBasicAuth(login, password)).json()["objects"]
        for i in blocked_user:
            blocked_user_info = blocked_user[i]["message", "key", "fields"]
            print(blocked_user_info)

        os.remove(path_to_file)
        print("Файл удален.")
