import os
import test_values

from factory import create_serializer


def get_input_serializer(input_file_name, input_format):
    if input_format is None:
        _, input_format = os.path.splitext(input_file_name)
        input_format = input_format[1:]

    if not input_format.casefold() in ("json", "yaml", "toml"):
        print("Wrong input format")
        exit()

    return create_serializer(input_format)


def get_output_serializer(output_file_name, output_format):
    if output_format is None:
        _, output_format = os.path.splitext(output_file_name)
        output_format = output_format[1:]

    if not output_format.casefold() in ("json", "yaml", "toml"):
        print("Wrong output format")
        exit()

    return create_serializer(output_format)


def prepare_task_files():
    try:
        formats = ("json", "yaml")
        for file_format in formats:
            with open("test." + file_format, "w") as out_file:
                output_serializer = create_serializer(file_format)
                out_str = output_serializer.dumps(test_values.Test())
                out_file.write(out_str)

        with open("test.toml", "w") as out_file:
            output_serializer = create_serializer("toml")
            out_str = output_serializer.dumps(test_values.Example())
            out_file.write(out_str)
    except Exception:
        print("Output error")
