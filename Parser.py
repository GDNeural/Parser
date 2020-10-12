#!  python3
import json
import copy


def make_json():
    with open("cor-alpha-feed.log", 'r') as logs:
        with open("json.json", 'w') as output:
            json_form = []
            lines = logs.readlines()  # list_of_strings
            edited_arr = {}
            message = []
            for index, line in enumerate(lines):
                if index + 1 <= len(lines):
                    if line.find("WARN") != -1 or line.find("ERROR") != -1:
                        for x, y in (" [39m", "  "), (" [34m", "  "), (" [31m", "  "), (" [1;31m", "  "), \
                                    ("[0;39m [36m", "  "), ("[0;39m [32m", "  "), ("[0;39m ", "  "), ("[0m", ""):
                            line = line.replace(x, y)
                        line = line.replace(" [", "  [", 1)
                        delimited_list = line.split("  ", 4)
                        message.append(delimited_list[4][:-1])
                        edited_arr.update({"Data": delimited_list[0], "Level": delimited_list[2]})
                        counter = 1
                        while not lines[index+counter].startswith("2020"):
                            if lines[index+counter].startswith("Caused by"):
                                message.append(str(lines[index+counter][:-1]))
                                counter += 1
                            else:
                                counter += 1
                                continue
                        edited_arr.update({"Message": message})
                        if index > len(lines) - 1:
                            edited_arr.update({"Message": message})
                            continue
                        copi = copy.deepcopy(edited_arr)
                        json_form.append(copi)
                        edited_arr.clear()
                        message.clear()
                    else:
                        continue
            json.dump(json_form, output, indent=4, sort_keys=True)


make_json()
