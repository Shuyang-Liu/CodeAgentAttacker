import argparse
import ast
import datetime
import os
import pprint
import python_transformer
import utils


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
            Automatically Python code transformation.
            """,
    )
    parser.add_argument(
        "-s",
        "--src_file",
        dest="src_file",
        required=True,
        default=None,
        help="source file you need to transform.",
    )
    parser.add_argument(
        "-t",
        "--target_file",
        dest="target_file",
        required=True,
        default=None,
        help="target file to save after transformation.",
    )
    parser.add_argument(
        "-j",
        "--json",
        dest="json_file",
        required=True,
        default=None,
        help="save results into a json file.",
    )
    parser.add_argument(
        "-single",
        "--operator",
        dest="single_operator",
        required=False,
        default=None,
        type=str,
        help="specify single operator to run.",
    )
    parser.add_argument(
        "-all",
        "--all",
        dest="apply_all",
        required=False,
        action="store_true",
        help="apply all applicable operators (True/False).",
    )
    args = parser.parse_args()
    return args


def normalize_content(src_file):
    """
    original code -> ast(original code) -> unparse(ast(original code));
    to avoid unnecessary comparison between diff <orignal code, transformed code>,
    like double quote can be changed to single quote.
    """
    clear_original_content = utils.clear_string(utils.read_file(src_file))
    tree = ast.parse(clear_original_content)
    normalize_content = ast.unparse(tree)
    utils.write_file(src_file, normalize_content)
    return src_file


def main(src_file, target_file, single_operator, json_file, apply_all=False):
    file_id = src_file.split("/")[-1].split(".py")[0]
    print(f"[START] processing file: {src_file}")
    start = datetime.datetime.now()
    src_file = normalize_content(src_file)
    (
        transformed_code,
        applicable_operators,
        patch_path,
        exception,
        diff_output,
        patch_path,
    ) = (None, None, None, None, None, None)
    try:
        # if True:
        transformed_code, applicable_operators = python_transformer.initialize(
            src_file, single_operator, target_file, file_id, apply_all
        )
        if len(applicable_operators) > 0:
            patch_path = os.path.join(
                "/".join(target_file.split("/")[:-1]), f"{file_id}.patch"
            )
            utils.write_file(target_file, transformed_code)
            diff_output = utils.generate_patch(src_file, target_file, patch_path)
    except Exception as ex:
        print("Exception: {}".format(ex))

    end = datetime.datetime.now()
    total_time = (end - start).total_seconds()
    result = {
        "file_id": file_id,
        "src_file": src_file,
        "target_file": target_file,
        "single_operator": single_operator,
        "patch_path": patch_path,
        "applicable_operators": applicable_operators,
        "exception": exception,
        "total_time": total_time,
        "diff_output": diff_output,
        "original_code": utils.read_file(src_file),
        "transformed_code": transformed_code,
    }
    # pprint.pprint(result, indent=2)
    utils.write_json(json_file, result)
    print(f"[END] processing file: {src_file} Total Time: {total_time}")
    return result


def transform_single_operator(src_file, target_file, single_operator):
    result = main(src_file, target_file, single_operator, json_file)
    return result


def transform_all_operator(src_file, target_file):
    single_operator = None
    result = main(src_file, target_file, single_operator, json_file, apply_all=True)
    return result


if __name__ == "__main__":
    args = parse_args()
    src_file = args.src_file
    target_file = args.target_file
    json_file = args.json_file
    single_operator = args.single_operator
    apply_all = args.apply_all

    print(f"STARTING AT {datetime.datetime.now()}")
    if src_file and target_file:
        if single_operator:
            transform_single_operator(src_file, target_file, single_operator)
        elif apply_all and not single_operator:
            transform_all_operator(src_file, target_file)
    print(f"END AT {datetime.datetime.now()}")
