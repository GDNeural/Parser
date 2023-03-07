import re


class MobileFormatting:

    @classmethod
    def format_tel(cls, tel):
        tel = tel.removeprefix("+")
        tel = tel.removeprefix("7")
        tel = tel.removeprefix("8")  # remove leading +,7,8
        tel = re.sub("[ ()-]", '', tel)  # remove space, (), -

        assert (len(tel) == 10)
        return tel
