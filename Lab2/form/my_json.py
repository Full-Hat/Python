import re

from serializer import Serializer

OBJECT_START_TOKEN = "{"
OBJECT_END_TOKEN = "}"
LIST_START_TOKEN = "["
LIST_END_TOKEN = "]"
TRUE_BOOL_TOKEN = "true"
FALSE_BOOL_TOKEN = "false"
NONE_TOKEN = "null"


class JsonFormat(Serializer):
    def serialize(self, basic_type):
        json_str = OBJECT_START_TOKEN
        for key in basic_type:
            value = basic_type[key]
            data_str = f"\"{str(key)}\": "
            if isinstance(value, bool):
                if value:
                    data_str += TRUE_BOOL_TOKEN
                else:
                    data_str += FALSE_BOOL_TOKEN
            elif isinstance(value, (int, float)):
                data_str += str(value)
            elif isinstance(value, bytes):
                integer_value = "bytes_" + str(len(value)) + "_" + str(int.from_bytes(value, "big"))
                data_str += f"\"{integer_value}\""
            elif isinstance(value, str):
                data_str += f"\"{value}\""
            elif isinstance(value, (list, tuple, set, frozenset)):
                current_str = self.__serialize_list_like_type(value)
                data_str += current_str
            elif isinstance(value, type(None)):
                data_str += NONE_TOKEN
            else:
                data_str += self.dumps(value)
            json_str += data_str + ", "
        if basic_type:
            json_str = json_str[:-2:]
        return json_str + OBJECT_END_TOKEN

    def __serialize_list_like_type(self, value):
        current_str = LIST_START_TOKEN
        for element in value:
            if isinstance(element, bool):
                if element:
                    current_str += TRUE_BOOL_TOKEN
                else:
                    current_str += FALSE_BOOL_TOKEN
            elif isinstance(element, bytes):
                integer_element = "bytes_" + str(len(element)) + "_" + str(int.from_bytes(element, "big"))
                current_str += f"\"{integer_element}\""
            elif isinstance(element, (int, float)):
                current_str += str(element)
            elif isinstance(element, str):
                current_str += f"\"{element}\""
            elif isinstance(element, (list, set, frozenset, tuple)):
                current_str += f"{self.__serialize_list_like_type(element)}"
            elif isinstance(element, type(None)):
                current_str += NONE_TOKEN
            else:
                current_str += self.dumps(element)
            current_str += ","
        if value:
            current_str = current_str[:-1:]
        return current_str + LIST_END_TOKEN

    def deserialize(self, format_str):
        format_str = format_str[1:-1]
        str_items = self.__find_items(format_str)
        result = self.make_dict_json(str_items)
        return result

    def __find_items(self, json_str):
        str_items = []
        str_item = ""
        stack_brackets = []
        stack_square_brackets = []
        stack_quotes = []
        for i in range(len(json_str)):
            if json_str[i] == "\"":
                if len(stack_quotes) == 0:
                    stack_quotes.append("\"")
                else:
                    stack_quotes.pop()
            if len(stack_quotes) == 0:
                if json_str[i] == OBJECT_START_TOKEN:
                    stack_brackets.append(OBJECT_START_TOKEN)
                if json_str[i] == OBJECT_END_TOKEN:
                    stack_brackets.pop()
                if json_str[i] == LIST_START_TOKEN:
                    stack_square_brackets.append(LIST_START_TOKEN)
                if json_str[i] == LIST_END_TOKEN:
                    stack_square_brackets.pop()
            if json_str[i] == "," and not (len(stack_brackets)) and not (len(stack_square_brackets)):
                str_items.append(str_item)
                str_item = ""
                continue
            str_item += json_str[i]
        str_items.append(str_item)
        return str_items

    def make_dict_json(self, my_str_items):
        my_dict = {}
        if len(my_str_items) != 0:
            my_str_items[0] = " " + my_str_items[0]
            for item in my_str_items:
                key_value = item.split(": ", 1)
                if len(key_value) == 2:
                    key_value[0] = key_value[0][2:len(
                        key_value[0]) - 1]
                    key_value[1] = self.__parse_value(key_value[1])
                    my_dict[key_value[0]] = key_value[1]
        return my_dict

    def __parse_value(self, my_value):
        if my_value[:7] == '"bytes_':
            str_intger = re.findall(r'_\d+_', my_value)[0]
            count_bytes = int(str_intger[1:len(str_intger) - 1])
            str_intger = re.findall(r"_\d+", my_value)[1]
            integer_value = int(str_intger[1:])
            my_value = integer_value.to_bytes(count_bytes, "big")
            return my_value
        elif my_value[0] == '"':
            my_value = my_value[1:len(my_value) - 1]
            return my_value
        elif my_value == TRUE_BOOL_TOKEN:
            return True
        elif my_value == FALSE_BOOL_TOKEN:
            return False
        elif my_value[0] == LIST_START_TOKEN:
            my_list = []
            my_value = my_value[1:len(my_value) - 1]
            my_str = ""
            stack_bracket = []
            stack_square_bracket = []
            stack_quotes = []
            for i in range(len(my_value)):
                if my_value[i] == "\"":
                    if len(stack_quotes) == 0:
                        stack_quotes.append("\"")
                    else:
                        stack_quotes.pop()
                if len(stack_quotes) == 0:
                    if my_value[i] == OBJECT_START_TOKEN:
                        stack_bracket.append(OBJECT_START_TOKEN)
                    if my_value[i] == OBJECT_END_TOKEN:
                        stack_bracket.pop()
                    if my_value[i] == LIST_START_TOKEN:
                        stack_square_bracket.append(LIST_START_TOKEN)
                    if my_value[i] == LIST_END_TOKEN:
                        stack_square_bracket.pop()
                if my_value[i] == ',' and len(stack_quotes) == 0 and len(stack_bracket) == 0 and len(
                        stack_square_bracket) == 0:
                    if my_str[0] == " ":
                        my_str = my_str[1:len(my_str)]
                    result = self.__parse_value(my_str)
                    my_list.append(result)
                    my_str = ""
                    continue
                my_str += my_value[i]
            if len(my_str) != 0:
                if my_str[0] == " ":
                    my_str = my_str[1:len(my_str)]
                my_list.append(self.__parse_value(my_str))
            return my_list
        elif my_value[0] == OBJECT_START_TOKEN:
            return self.deserialize(my_value)
        elif my_value == NONE_TOKEN:
            return None
        for i in range(len(my_value)):
            if my_value[i] == ".":
                return float(my_value)
        return int(my_value)
