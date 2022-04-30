import inspect
import types
from abc import ABC, abstractmethod
from types import FunctionType, CodeType

SIMPLE_TYPES = (int, float, bool, str, bytes, type(None))
SIMPLE_COLLECTION_TYPES = (list, tuple, dict, set, frozenset)


class Serializer(ABC):
    def dump(self, obj, file):
        dumps = self.dumps(obj)
        file.write(dumps)

    def dumps(self, obj):
        if inspect.isclass(obj):
            return self.dumps(self.__deconstruct_class(obj))
        elif inspect.isfunction(obj):
            return self.dumps(self.__deconstruct_function(obj))
        elif isinstance(obj, dict):
            return self.serialize(obj)
        else:
            obj_dict = self.__deconstruct_object(obj)
            return self.serialize(obj_dict)

    def load(self, file):
        return self.loads(file.read())

    def loads(self, format_str):
        result = {}
        flag_have_object = False
        if format_str != "":
            result = self.deserialize(format_str)
            for key, value in result.items():
                if key == "__object_type__":
                    flag_have_object = True
                    result[key] = self.__build_class(value)
                elif key == "__init__":
                    result = self.__build_class(result)
                elif key == "__code__":
                    result = self.__build_function(result)
            if flag_have_object:
                instance = result["__object_type__"]()
                instance.__dict__ = result["__dict__"]
                return instance
        return result

    @abstractmethod
    def serialize(self, basic_type):
        pass

    @abstractmethod
    def deserialize(self, format_str):
        pass

    def __deconstruct_object(self, obj):
        return {"__object_type__": self.__deconstruct_class(type(obj)), "__dict__": obj.__dict__}

    def __deconstruct_function(self, func):
        code_members = {}
        for key, value in inspect.getmembers(func.__code__):
            if key.startswith("co_") and key != "co_lines" and key != "co_linetable":
                code_members[key] = value

        globs = {}
        for element in code_members["co_names"]:
            if element in func.__globals__:
                value = func.__globals__[element]
            else:
                continue
            if element == func.__name__:
                globs[element] = element
            elif isinstance(value, SIMPLE_TYPES):
                globs[element] = value
            elif isinstance(value, SIMPLE_COLLECTION_TYPES):
                globs[element] = value
            elif inspect.isclass(value):
                globs[element] = self.__deconstruct_class(value)
            elif inspect.ismodule(value):
                globs[value.__name__] = "__module__"
            elif inspect.isfunction(value):
                globs[element] = self.__deconstruct_function(value)
            else:
                globs[element] = self.__deconstruct_object(value)

        closures = []
        if func.__closure__ is not None:
            for item in func.__closure__:
                if inspect.isfunction(item.cell_contents):
                    closures.append(self.__deconstruct_function(item.cell_contents))
                elif inspect.isclass(item.cell_contents):
                    closures.append(self.__deconstruct_class(item.cell_contents))
                elif isinstance(item.cell_contents, (SIMPLE_TYPES, SIMPLE_COLLECTION_TYPES)):
                    closures.append(item.cell_contents)
                else:
                    closures.append(self.__deconstruct_object(item.cell_contents))

        return {"__name__": func.__name__,
                "__code__": code_members,
                "__globals__": globs,
                "__defaults__": func.__defaults__,
                "__closure__": closures}

    def __deconstruct_class(self, obj):
        result_dict = {"__name__": obj.__name__}
        for key, value in inspect.getmembers(obj):
            if key.startswith("__") and key != "__init__":
                continue
            if inspect.ismethod(value):
                result_dict[key] = self.__deconstruct_function(value.__func__)
            elif isinstance(value, (SIMPLE_TYPES, SIMPLE_COLLECTION_TYPES)):
                result_dict[key] = value
            elif inspect.isfunction(value):
                result_dict[key] = self.__deconstruct_function(value)
            elif inspect.isclass(value):
                result_dict[key] = self.__deconstruct_class(value)
            else:
                result_dict[key] = self.__deconstruct_object(value)
        return result_dict

    def __build_function(self, func_dict):
        dict_argument = {}

        for key, value in func_dict['__code__'].items():
            if isinstance(value, list):
                value = self.__convert_tuple(value)
            dict_argument[key] = value

        recursion = False
        for key, value in func_dict['__globals__'].items():
            flag_have_object = False

            if value == func_dict['__name__']:
                recursion = True
                continue

            elif value == "__module__":
                func_dict["__globals__"][key] = __import__(key)

            elif isinstance(value, dict):
                for master_key, master_value in value.items():
                    if master_key == "__object_type__":
                        flag_have_object = True
                        func_dict["__globals__"][key][master_key] = self.__build_class(master_value)
                    if master_key == "__init__":
                        func_dict['__globals__'][key] = self.__build_class(value)
                    if master_key == "__code__":
                        func_dict["__globals__"][key] = self.__build_function(value)
                if flag_have_object:
                    instance = func_dict["__globals__"][key]["__object_type__"]()
                    instance.__dict__ = func_dict["__globals__"][key]["__dict__"]
                    func_dict["__globals__"][key] = instance
        func_dict['__globals__']['__builtins__'] = __builtins__

        code = CodeType(dict_argument["co_argcount"],
                        dict_argument["co_posonlyargcount"],
                        dict_argument["co_kwonlyargcount"],
                        dict_argument["co_nlocals"],
                        dict_argument["co_stacksize"],
                        dict_argument["co_flags"],
                        dict_argument["co_code"],
                        tuple(dict_argument["co_consts"]),
                        tuple(dict_argument["co_names"]),
                        tuple(dict_argument["co_varnames"]),
                        dict_argument["co_filename"],
                        dict_argument["co_name"],
                        dict_argument["co_firstlineno"],
                        dict_argument["co_lnotab"],
                        tuple(dict_argument["co_freevars"]),
                        tuple(dict_argument["co_cellvars"]))

        closure_cells = []
        if func_dict.get('__closure__') is not None:
            for item in func_dict['__closure__']:
                flag_have_object = False
                if isinstance(item, dict):
                    cell_item = item
                    for master_key, value in item.items():
                        if master_key == "__object_type__":
                            flag_have_object = True
                            item[master_key] = self.__build_class(value)
                        elif master_key == "__init__":
                            cell_item = self.__build_class(item)
                        elif master_key == "__code__":
                            cell_item = self.__build_function(item)
                    if flag_have_object:
                        instance = item["__object_type__"]()
                        instance.__dict__ = item["__dict__"]
                        closure_cells.append(instance)
                    else:
                        closure_cells.append(cell_item)
                else:
                    closure_cells.append(item)
        closure_cells = [types.CellType(element) for element in closure_cells]
        closure_cells = tuple(closure_cells)

        func = FunctionType(code, func_dict['__globals__'], func_dict['__name__'],
                            self.__convert_tuple(func_dict.get('__defaults__')), closure_cells)
        if recursion:
            func.__globals__[func_dict['__name__']] = func
        return func

    def __convert_tuple(self, obj):
        if obj is not None:
            for i in range(len(obj)):
                if isinstance(obj[i], list):
                    obj[i] = self.__convert_tuple(obj[i])
            return tuple(obj)
        else:
            return ()

    def __build_class(self, class_dict):
        for key, value in class_dict.items():
            flag_have_object = False
            if isinstance(value, dict):
                for master_key, master_value in value.items():
                    if master_key == "__object_type__":
                        flag_have_object = True
                        class_dict[key][master_key] = self.__build_class(master_value)
                    if master_key == "__init__":
                        class_dict[key] = self.__build_class(value)
                    if master_key == "__code__":
                        class_dict[key] = self.__build_function(value)

                if flag_have_object:
                    instance = class_dict[key]["__object_type__"]()
                    instance.__dict__ = class_dict[key]["__dict__"]
                    class_dict[key] = instance
        instance = type(class_dict["__name__"], (), class_dict)
        return instance
