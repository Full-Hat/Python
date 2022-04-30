import argparse
import utils


if __name__ == "__main__":
    # Parse args
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("-in", "--input", required=True, default=None)
    arg_parser.add_argument("-out", "--output", required=True, default=None)
    arg_parser.add_argument("-inf", "--inp-format", required=False, default=None)
    arg_parser.add_argument("-outf", "--out-format", required=False, default=None)

    res = arg_parser.parse_args()

    # Init serializer
    # input_serializer = utils.get_input_serializer(res.input, res.inp_format)
    # output_serializer = utils.get_output_serializer(res.output, res.out_format)

    utils.prepare_task_files()

    '''# Serialize
    try:
        with open(res.input, "r") as in_file:
            file_content = in_file.read()
            input_obj = input_serializer.loads(file_content)
    except Exception:
        print("Input error")

    # Deserialize
    try:
        with open(res.output, "w") as out_file:
            out_str = output_serializer.dumps(input_obj)
            out_file.write(out_str)
    except Exception:
        print("Output error")'''
