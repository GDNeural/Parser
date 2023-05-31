import re


class MobileFormatting:

    @classmethod
    def format_tel(cls, tel):
        if tel:
            tel = tel.removeprefix("+")
            tel = tel.removeprefix("8")  # remove leading +,8
            tel = re.sub("[ ()-]", '', tel)  # remove space, (), -
            if len(tel) == 10:
                return f"7{tel}"
            elif len(tel) == 11:
                return tel
            else:
                raise ValueError('Invalid phone number')
        raise ValueError('Phone number is null')
