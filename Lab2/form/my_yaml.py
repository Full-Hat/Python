import re

from serializer import Serializer


class YamlFormat(Serializer):

    def serialize(self, basic_type):
        array_rows = ['---']

        for key in basic_type:
            value = basic_type[key]
            yaml_str = f"{str(key)}: "

            if isinstance(value, bool):

                if value:
                    yaml_str += "true"

                else:
                    yaml_str += "false"

            elif isinstance(value, (int, float)):
                yaml_str += str(value)

            elif isinstance(value, bytes):
                integer_element = str(int.from_bytes(value, "big"))
                yaml_str += f"!!bytes{str(len(value))} {integer_element}"

            elif isinstance(value, str):

                if len(value) != 0:
                    yaml_str += value

                else:
                    yaml_str += "\'\'"

            elif isinstance(value, (list, set, tuple, frozenset)):

                if len(value) != 0:
                    buffer_str = self.make_str_list(value)
                    array_rows.append(yaml_str)
                    array_rows += buffer_str
                    continue

                else:
                    yaml_str += "[]"

            elif value is None:
                yaml_str += "!!null null"

            else:
                dict_str = self.dumps(value).split("\n")
                dict_str = dict_str[1:len(dict_str) - 1]

                if len(dict_str) != 0:
                    buffer_str = list(map(lambda st: "  " + st, dict_str))
                    array_rows.append(yaml_str)  # Need add a type of class, later
                    array_rows += buffer_str
                    continue

                else:
                    yaml_str += "{}"

            array_rows.append(yaml_str)

        array_rows.append('...')

        return "\n".join(array_rows)

    def make_str_list(self, value):
        array_str = []

        for element in value:

            if isinstance(element, bool):

                if element:
                    array_str.append("- true")
                else:
                    array_str.append("- false")

            elif isinstance(element, bytes):
                integer_element = str(int.from_bytes(element, "big"))
                array_str.append(f"- !!bytes{str(len(element))} {integer_element}")

            elif isinstance(element, (int, float)):
                array_str.append("- " + str(element))

            elif isinstance(element, str):

                if element != "":
                    array_str.append("- " + element)

                else:
                    array_str.append("- ''")

            elif isinstance(element, (list, set, frozenset, tuple)):

                if len(element) != 0:
                    buffer_str = self.make_str_list(element)
                    buffer_str = list(map(lambda st: "  " + st, buffer_str))
                    buffer_str[0] = "-" + buffer_str[0][1:]
                    array_str += buffer_str

                else:
                    array_str.append("- []")

            elif isinstance(element, type(None)):
                array_str.append("- !!null null")

            else:
                buffer_str = self.dumps(element).split("\n")

                if len(buffer_str) != 0:
                    buffer_str = buffer_str[1:len(buffer_str) - 1]
                    array_str.append(f"- {buffer_str[0]}")
                    buffer_str = list(map(lambda st: "  " + st, buffer_str[1:]))
                    array_str += buffer_str

                else:
                    array_str.append("- {}")

        return array_str

    def deserialize(self, array_yaml):

        if isinstance(array_yaml, str):
             array_yaml = array_yaml.split("\n")

        my_dict = {}
        count = 0

        for item in array_yaml:

            key_value = item.split(": ", 1)

            if array_yaml[count][0] == " " or array_yaml[count][0] == "-":  # start index of string must be null, either we will skip a string
                count += 1
                continue

            if len(key_value) == 2:

                if key_value[1] != "" and (key_value[1][:2] != "!!" or key_value[1][:7] != "!!bytes" or key_value[1][:6] != "!!null"):
                    my_dict[key_value[0]] = self.define_type(key_value[1])

                else:
                    current_buffer = []
                    next_index = 0

                    if array_yaml[count + 1][0] == " ":
                        next_index = re.search(r'\s+', array_yaml[count + 1])  # check a next index of string in array, that deside what type of collection will

                    if next_index:
                        next_index = len(next_index.group(0))

                    if next_index == 0:
                        current_buffer = self.find_array_list(array_yaml[count + 1:])
                        stuff = self.make_collection_list(current_buffer)
                        my_dict[key_value[0]] = stuff

                    else:

                        for element in array_yaml[count + 1:]:
                            current_index = re.search(r'\s+', element)

                            if current_index:

                                if len(current_index.group(0)) < next_index:
                                    break

                                else:
                                    current_buffer.append(element[next_index:])

                        my_dict[key_value[0]] = self.deserialize(current_buffer)

            count += 1

        return my_dict

    def find_array_list(self, array_yaml):
        current_buffer = []

        for element in array_yaml:

            if element[:2] != "- " and element[:2] != "  ":
                break

            elif element[:4] == "- - " or re.match(r'-\s\S+:',element):  # save element with "- - ", that understand where have a nested list/save element with "- ...: ", that understand where nested dictionary
                current_buffer.append(element)

            else:
                current_buffer.append(element[2:])

        return current_buffer

    def define_type(self, obj):

        if re.match(r"0x[0-9A-z]", obj):

            return float.fromhex(obj)

        elif re.match(r"[\-0-9]+\.[0-9]+", obj):

            return float(obj)

        elif re.match(r"[0-9]+", obj):

            return int(obj)

        elif obj == "true":

            return True

        elif obj == "false":

            return False

        elif obj[:7] == "!!bytes":
            buffer_integers = re.findall(r"[0-9]+", obj)
            count_bytes = int(buffer_integers[0])
            integer = int(buffer_integers[1])
            item_bytes = integer.to_bytes(count_bytes, "big")

            return item_bytes

        elif obj[:6] == "!!null":

            return None

        elif obj == "[]":

            return []

        elif obj == "{}":

            return {}

        elif obj == "\'\'":

            return ""

        else:

            return obj

    def make_collection_list(self, current_array):
        my_list = []
        count = 0
        flag_active = False

        for item in current_array:

            if (current_array[count][0] == " " or (current_array[count][:2] == "- " and current_array[count][:4] != "- - " and not (re.match(r'-\s\S+:', item))) or re.match(r'[^-\s]+:',item)):  # start index of string must be null, either we will skip a string
                if flag_active:
                    count += 1
                    continue

            flag_active = False

            if item[:2] != "- ":
                my_list.append(self.define_type(item))

            elif item[:4] == "- - ":
                current_buffer = [item[4:len(
                    item)]]  # place a first item in beginnig by itself, because of first part "- - "  at first part need cut cut out

                for element in current_array[count + 1:]:

                    if (element[:4] == "- - " or element[:2] != "- ") and element[:2] != "  ":
                        break

                    else:
                        current_buffer.append(element[2:])

                stash = self.make_collection_list(current_buffer)
                my_list.append(stash)
                flag_active = True

            elif re.match(r'-\s\S+:', item):
                current_buffer = [item[2:]]

                for element in current_array[count + 1:]:

                    if re.match(r'[^-]+:', element) or re.match(r'-\s[^:]+\Z', element) or element[:2] == "  ":
                        current_buffer.append(element)
                    else:
                        break

                my_list.append(self.deserialize(current_buffer))
                flag_active = True

            count += 1

        return my_list
