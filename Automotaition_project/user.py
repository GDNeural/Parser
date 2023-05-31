import transliterate
from mob_form import MobileFormatting


class User:

    def __init__(self, data):
        self.f_name = data.get("fields", {}).get("first_name", None)
        self.l_name = data.get("fields", {}).get("last_name", None)
        self.mid_name = data.get("fields", {}).get("middle_name", None)
        self.fio = transliterate.transliterate(str.lower(self.l_name + self.f_name[0] + self.mid_name[0]))
        self.position = data.get("fields", {}).get("position", None)
        self.tab_nom = data.get("fields", {}).get("tabnom", None)
        self.org = data.get("fields", {}).get("org", None)
        self.mob_phone = data.get("fields", {}).get("mobile", None)

        if data.get("fields", {}).get("email", None):
            self.email = data.get("fields", {}).get("email")
        else:
            self.email = f"{self.fio}@cash-u.com"

        # FORM_A_PROFILE_LIST_TO_USERS_ROLE

    def get_org_id(self):
        organization_choice = {"ООО ": 1, "МКК ": 2, "ИП": 3}

        org_id = organization_choice[self.org]

        return org_id

    def get_user_first_name(self):
        return self.f_name

    def get_user_last_name(self):
        return self.l_name

    def get_user_fio(self):
        return self.fio

    def get_user_position(self):
        return self.position

    def get_user_tab_nom(self):
        return self.tab_nom

    def get_user_email(self):
        return self.email

    def get_user_mobile(self):
        return self.mob_phone
