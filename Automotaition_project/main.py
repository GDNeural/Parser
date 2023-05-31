import json
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from sms_sender import SigmaSMS
from user import User
from mail_sender import Email
from keycloak import Keycloak
from user_block import user_block
from mob_form import MobileFormatting

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# PATH_TO_USER_FILES
path_to_json_folder = os.environ['ITOP_JSON_DIRECTORY']
list_of_files = os.listdir(path_to_json_folder)

# ITOP_API_CONNECT_CREDENTIALS
php_version = os.environ['ITOP_PHP_VERSION']
itop_login = os.environ['ITOP_LOGIN']
itop_pwd = os.environ['ITOP_PASSWORD']

dict_profile_to_id = {"Administrator": 1, "Portal user": 2, "Configuration Manager": 3, "Service Desk Agent": 4,
                      "Support Agent": 5, "Problem Manager": 6, "Change Implementor": 7, "Change Supervisor": 8,
                      "Change Approver": 9, "Service Manager": 10, "Document author": 11, "Portal power user": 12,
                      "REST Services User": 1024}
keycloak = Keycloak()
acc_token = keycloak.get_access_token()

# WORK_WITH_JSON+CONNECTION_STRING_MAKER
with os.scandir(path_to_json_folder) as it:
    for entry in it:
        if entry.name.endswith(".json") and entry.is_file():
            # for file in list_of_files:
            path_to_file = path_to_json_folder + entry.name
            with open(path_to_file, "r", encoding='utf-8') as file:
                user_data = json.load(file)
                if user_data["operation"] == "core/create":
                    user = User(user_data)
                    kc_response = keycloak.register_user(fio, email, f_name, l_name, pwd_for_user, acc_token)
                    # FORM_A_PROFILE_LIST_TO_USERS_ROLE
                    profile_list = [{"profileid": 2}]

                    try:
                        MobileFormatting.format_tel(user.get_user_mobile())
                    except ValueError:
                        print(f"User {user.get_user_fio()} phone number is null")
                        continue

                    ## KEYCLOAK PART
                    kc_response = keycloak.register_user(fio, email, f_name, l_name, pwd_for_user, acc_token)
                    print(kc_response)
                    if kc_response.status_code == 409:
                        print("User already exists in keycloak.")
                        continue

                    ## ITOP PART
                    # FORM_URLS_FOR_SENDING

                    person_create_url = "https://itop.cunet.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s" \
                                        "&json_data={\"operation\": \"core/create\", \"comment\": \"Adding new user\", \"class\": " \
                                        "\"Person\", \"output_fields\": \"friendlyname, email\",\"fields\": {\"name\": \"%s\", " \
                                        "\"first_name\": \"%s\", \"email\": \"%s\", \"mobile_phone\": \"%s\", " \
                                        "\"employee_number\": \"%s\", \"function\": \"%s\",\"org_id\": \"%s\"}}" % \
                                        (php_version, itop_login, itop_pwd, l_name, f_name, email, mob_phone,
                                         tab_nom, position, org_id)

                    ext_usr_create_url = "https://itop.cunet.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s" \
                                         "&json_data={\"operation\": \"core/create\",\"comment\": \"Adding new user\", " \
                                         "\"class\": \"UserExternal\", \"output_fields\": \"login, email\",\"fields\":" \
                                         "{\"login\": \"%s\", \"language\": \"%s\", \"profile_list\": %s}} " % \
                                         (php_version, itop_login, itop_pwd, fio, language, json.dumps(profile_list))

                    # Делаем POST запрос на создание Person, получаем назад contactid
                    person_id = ""
                    user_id = ""

                    person_for_id = requests.request("POST", person_create_url, auth=HTTPBasicAuth(itop_login, itop_pwd)).json()["objects"]
                    print(person_for_id)

                    for i in person_for_id:
                        person_id = person_for_id[i]["key"]

                    # POST_REQUEST_FOR_CREATION
                    user = requests.request("POST", ext_usr_create_url, auth=HTTPBasicAuth(itop_login, itop_pwd)).json()["objects"]
                    print(user)

                    for i in user:
                        user_id = user[i]["key"]


                    # FORM_URL_FOR_CREATING_CONNECTION+SENDING

                    put_together_url = "https://itop.cunet.ru/webservices/rest.php?version=%s&auth_user=%s&auth_pwd=%s" \
                                       "&json_data={\"operation\": \"core/update\",\"comment\": " \
                                       "\"Adding Persona to new user\", \"class\": \"UserExternal\", \"key\":\"%s\", " \
                                       "\"output_fields\": \"login, email\", \"fields\": {\"contactid\": \"%s\"}} " % \
                                       (php_version, itop_login, itop_pwd, user_id, person_id)

                    result = requests.request("PUT", put_together_url, auth=HTTPBasicAuth(itop_login, itop_pwd)).json()
                    print(result)

                    # COPIYNG TO FOLDER AND DELETE
                    if 'mob_phone' in locals():
                        response = SigmaSMS.send_message(mob_phone, 'Доступ к порталу поддержки. login: %s , '
                                                                    'temp_password: %s' % (fio, pwd_for_user))
                        print(response)
                    else:
                        print('No message sent')

                    Email.send_message(email, f_name, email, pwd_for_user)

                    os.popen('cp %s %s' % (path_to_file, path_to_json_folder + '/archive'))
                    os.popen('rm -r --interactive=never -- "%s"' % path_to_file)
                    print("Файл удален.")

                elif user_data["operation"] == "core/lock":
                    user_block(path_to_file)
