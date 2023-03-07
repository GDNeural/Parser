import transliterate
import json
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from sms_sender import SigmaSMS
from mob_form import MobileFormatting

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# PATH_TO_USER_FILES
path_to_json_folder = os.environ['ITOP_JSON_DIRECTORY']
list_of_files = os.listdir(path_to_json_folder)

# ITOP_API_CONNECT_CREDENTIALS
php_version = os.environ['ITOP_PHP_VERSION']
itop_login = os.environ['ITOP_LOGIN']
itop_pwd = os.environ['ITOP_PASSWORD']

# KEYCLOAK_API_CONNECT_CREDENTIALS
kc_client_id = os.environ['KEYCLOAK_CLIENT_ID']
kc_secret = os.environ['KEYCLOAK_CLIENT_SECRET']
kc_username = os.environ['KEYCLOAK_USERNAME']
kc_pwd = os.environ['KEYCLOAK_PASSWORD']

# INFORMATION_DICTIONARIES
dict_organisation_to_id = {"ООО Кибертех": 1, "ООО МКК \"Киберлэндинг\"": 2, "ИП Слезин": 3, "ООО Крауд": 4,
                           "ООО МАД софт": 5, "НБКИ": 6, "Эквифакс": 7, "ИНТИС": 8, "SIGMA messaging": 9,
                           "ООО Киберколлект": 10, "ТрансКапиталБанк": 11, "Альфабанк": 12, "IDX": 13,
                           "DAIMA": 14, "DADATA": 15}

dict_profile_to_id = {"Administrator": 1, "Portal user": 2, "Configuration Manager": 3, "Service Desk Agent": 4,
                      "Support Agent": 5, "Problem Manager": 6, "Change Implementor": 7, "Change Supervisor": 8,
                      "Change Approver": 9, "Service Manager": 10, "Document author": 11, "Portal power user": 12,
                      "REST Services User": 1024}

# dict_function_to_profile_ids = {
#     "Специалист ": [2, 11],
#     "Старший специалист": [2, 9, 11],
#     "Эксперт по вознаграждению C&B (компенсация и бенефиты)": [2, 11]
# }
kc_token_url = "https://kc.cunet.ru/realms/master/protocol/openid-connect/token"
data = {
    "username": kc_username,
    "password": kc_pwd,
    "client_id": kc_client_id,
    "client_secret": kc_secret,
    "grant_type": "password"
}
acc_token = requests.request("POST", kc_token_url, data=data).json()["access_token"]

# WORK_WITH_JSON+CONNECTION_STRING_MAKER
with os.scandir(path_to_json_folder) as it:
    for entry in it:
        if entry.name.endswith(".json") and entry.is_file():
            # for file in list_of_files:
            path_to_file = path_to_json_folder + entry.name
            with open(path_to_file, "r", encoding='utf-8') as file:
                user_info = json.load(file)["fields"]

                # GETTING_TAGS_FROM_USER_INFO
                f_name = user_info["first_name"]
                l_name = user_info["last_name"]
                mid_name = user_info["middle_name"]
                fio = transliterate.transliterate(str.lower(l_name + f_name[0] + mid_name[0]))
                position = user_info["position"]
                tab_nom = user_info["tabnom"]
                email = "%s@cash-u.com" % fio
                org_id = str(dict_organisation_to_id[user_info["org"]])
                language = "RU RU"
                pwd_for_user = "12345Qwerty!"

                ### Необходимо привести к единому формату
                if user_info["mobile"]:
                    mob_phone = "7%s" % (MobileFormatting.format_tel(user_info["mobile"]))
                    print(mob_phone)
                else:
                    print("Phone number for user %s is null" % fio)

                # FORM_A_PROFILE_LIST_TO_USERS_ROLE
                profile_list = [{"profileid": 2}]
                # for i in dict_function_to_profile_ids[position]:
                #     profile_list.append({"profileid": i})
                ## KEYCLOAK PART

                usr_create_data = {
                    "enabled": True,
                    "username": fio,
                    "email": email,
                    "firstName": f_name,
                    "lastName": l_name,
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
                kc_url = "https://kc.cunet.ru/admin/realms/itop/users"
                response = requests.request("POST", kc_url, headers=headers, data=json.dumps(usr_create_data))
                print(response)

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
                print(ext_usr_create_url)
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
                # COPIYNG TO FOLDER AND DELETE
                if 'mob_phone' in locals():
                    response = SigmaSMS.send_message(mob_phone, 'Доступ к порталу поддержки. login: %s , '
                                                                'temp_password: %s' % (fio, pwd_for_user))
                    print(response)
                else:
                    print('No message sent')

                os.popen('cp %s %s' % (path_to_file, path_to_json_folder + '/archive'))
                os.remove('rm -r --interactive=never -- "./$filename"')
                print("Файл удален.")