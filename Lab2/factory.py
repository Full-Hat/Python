from form.my_json import JsonFormat
from form.my_toml import TomlFormat
from form.my_yaml import YamlFormat


def create_serializer(name: str):
    if name.casefold() == "json":
        return JsonFormat()
    elif name.casefold() == "yaml":
        return YamlFormat()
    elif name.casefold() == "toml":
        return TomlFormat()
    else:
        raise NameError("Unknown serializer name")
