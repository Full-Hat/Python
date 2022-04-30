import re
from enum import Enum

from serializer import Serializer


class CollectionType(Enum):
    simple_list = 0,
    complex_list = 1,
    dictionary = 2


class TomlFormat(Serializer):

    def serialize(self, obj):
        result = []
        root_var_stack = []
        self.serialize_complex_type(obj, "", result, root_var_stack)
        result = list(filter(lambda x: x is not None, result))
        return ''.join(result)

    def deserialize(self, my_str):
        temp_str = my_str
        result = {}

        tokens = [
            "(\w+) = [(.+)]",
            "(\w+) = (.+)\n",
            "(\[+)(.+)(\]+)\n",
            "\n",
        ]

        curr = result

        while True:

            findings = [re.match(token, temp_str) for token in tokens]


            if not any(findings) or len(temp_str) == 0:
                break

            index = 0
            for i in range(len(findings)):
                if findings[i]:
                    index = i
                    break

            if index == 0:
                curr[findings[index].group(0)] = list(
                    map(lambda x: self.get_var(x), findings[index].group(2).split(", ")))
            elif index == 1:
                if findings[index].group(2).startswith("["):
                    str_list = findings[index].group(2)[1:-1]
                    l = []
                    l_stack = [l]
                    while True:
                        f = [None, None]

                        for i in range(len(str_list)):
                            if str_list[i] == "[":
                                f[0] = i
                                break

                            elif str_list[i] == "]":
                                f[1] = i
                                break

                        if len(str_list) == 0:
                            break

                        if f[0]:
                            for t in str_list[0: f[0]].split(", "):
                                if t != "":
                                    l_stack[-1].append(self.get_var(t))

                            str_list = str_list[f[0] + 1: len(str_list)]

                            child_list = []
                            l.append(child_list)
                            l_stack.append(child_list)
                        elif f[1]:
                            for t in str_list[0: f[1]].split(", "):
                                if t != "":
                                    l_stack[-1].append(self.get_var(t))

                            str_list = str_list[f[1] + 1: len(str_list)]
                            l_stack.pop()
                        else:
                            for t in str_list.split(", "):
                                if t != "":
                                    l_stack[-1].append(self.get_var(t))
                            break

                    curr[findings[index].group(1)] = l
                else:
                    curr[findings[index].group(1)] = self.get_var(findings[index].group(2))
            elif index == 2:
                brackets = findings[index].group(0).count("[")
                hierarhy = findings[index].group(2).split(".")

                curr = result
                for item in hierarhy:
                    try:
                        curr = curr[item]
                    except:
                        if brackets == 2:
                            d = {}
                            curr.append(d)
                            curr = d

                        elif brackets == 1:
                            curr[item] = {}

                        curr = curr[item]

                if brackets == 2:
                    d = {}
                    curr.append(d)
                    curr = d

            elif index == 3:
                if isinstance(curr, list):
                    pass

                curr = result

            temp_str = temp_str[findings[index].span()[1]: len(temp_str)]

        return result

    def serialize_complex_type(self, obj, last_mark, result, root_var_stack):
        curr = obj

        if isinstance(obj, dict):
            if len(obj) == 0:
                curr_mark = self.get_collection_atr(root_var_stack)
                if last_mark != curr_mark:
                    result.append(curr_mark)
                    last_mark = curr_mark
                result.append("\n")

            curr = obj.items()

        if isinstance(obj, list) or isinstance(obj, tuple):
            if len(obj) == 0:
                curr_mark = self.get_collection_atr(root_var_stack)
                if last_mark != curr_mark:
                    result.append(curr_mark)
                    last_mark = curr_mark
                result.append("\n")

        for i, item in enumerate(curr):
            value = item
            name = ""

            if isinstance(obj, dict):
                value = item[1]
                name = item[0]

            if self.is_symple_type(value):
                toml_repr = self.to_toml_var_format(value)

                curr_mark = self.get_collection_atr(root_var_stack)

                if last_mark != curr_mark:
                    result.append(curr_mark)
                    last_mark = curr_mark

                if name != "":
                    result.append(str(name) + " = " + str(toml_repr) + "\n")
                else:
                    result.append(str(toml_repr) + "\n")

            if isinstance(value, list) or isinstance(value, tuple):
                list_type = CollectionType.simple_list

                for item in value:
                    if isinstance(item, dict):
                        list_type = CollectionType.complex_list
                        break

                if list_type == CollectionType.simple_list:
                    toml_list = []

                    for var in value:
                        toml_list.append(self.to_toml_var_format(var))

                    result.append(str(name) + " = [" + ", ".join(toml_list) + "]\n")
                    continue

                root_var_stack.append((str(name), list_type))
                self.serialize_complex_type(value, last_mark, result, root_var_stack)
                result.append("\n")
                root_var_stack.pop()

            if isinstance(value, dict):
                root_var_stack.append((str(name), CollectionType.dictionary))
                self.serialize_complex_type(value, last_mark, result, root_var_stack)
                result.append("\n")
                root_var_stack.pop()

    def get_collection_atr(self, root_var_stack):
        if len(root_var_stack) != 0:
            a = [item[0] for item in root_var_stack]

            while "" in a:
                a.remove("")

            collection_name = ".".join(a) if len(a) > 1 else str(a[0])

            if collection_name.endswith("."):
                collection_name = collection_name[0: -1]

            if root_var_stack[-1][1] == CollectionType.complex_list:
                return "[[" + collection_name + "]]\n"

            if root_var_stack[-1][1] == CollectionType.dictionary:
                return "[" + collection_name + "]\n"

    def get_var(self, str_var):
        str_var = re.sub("\n|\"|'", "", str_var)

        if str_var == "[]":
            return []

        elif str_var == "{}":
            return {}

        elif str_var.startswith('bytes_'):
            count_str = re.findall(r'_\d+_', str_var)[0]  # bytes count
            count_bytes = int(count_str[1: len(count_str) - 1])
            int_repr = re.findall(r"_\d+", str_var)[1]  # get int repr
            int_val = int(int_repr[1:])
            return int_val.to_bytes(count_bytes, "big")

        elif "." in str_var:
            try:
                return float(str_var)
            except:
                pass
        elif str_var == "None":
            return None
        elif str_var == "true":
            return True
        elif str_var == "false":
            return False
        else:
            try:
                return int(str_var)
            except:
                pass
        return str_var

    def to_toml_var_format(self, value):
        toml_repr = value

        if isinstance(value, list) or isinstance(value, tuple):
            value = list(map(lambda x: self.to_toml_var_format(x), value))
            return "[" + ", ".join(value) + "]"

        elif isinstance(value, dict):
            return "{}"

        elif isinstance(value, str):
            if '\\' in value:
                toml_repr = "'" + value + "'"
            else:
                toml_repr = '"' + value + '"'

        elif isinstance(value, type(None)):
            toml_repr = '"None"'

        elif isinstance(value, bytes):
            toml_repr = '"bytes_' + str(len(value)) + "_" + str(int.from_bytes(value, "big")) + '"'

        elif isinstance(value, bool):
            if value:
                toml_repr = "true"
            else:
                toml_repr = "false"

        return str(toml_repr)

    def is_symple_type(self, value):

        if isinstance(value, int) or isinstance(value, float) or isinstance(value, str) or isinstance(value, type(None)) or isinstance(value, bytes) or isinstance(value, bool):
            return True

        return False

