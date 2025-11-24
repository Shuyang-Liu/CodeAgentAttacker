import ast
import csv
import difflib
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path
import numpy as np


class TextColor:
    HEADER = "\033[95m"
    ENDC = "\033[0m"


def generate_patch(file1_path, file2_path, patch_path, encoding="utf-8"):

    file1_text = Path(file1_path).read_text(encoding=encoding)
    file2_text = Path(file2_path).read_text(encoding=encoding)
    file1_lines = file1_text.splitlines()  # no trailing \n
    file2_lines = file2_text.splitlines()

    diff_iter = difflib.unified_diff(
        file1_lines, file2_lines, fromfile=file1_path, tofile=file2_path, lineterm=""
    )

    patch_content = "\n".join(diff_iter) + "\n"

    Path(patch_path).write_text(patch_content, encoding=encoding)
    return patch_content


def dump_json(file_path, data):
    def convert_sets(obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, dict):
            return {k: convert_sets(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_sets(i) for i in obj]
        return obj

    data = convert_sets(data)
    with open(file_path, "w") as fp:
        json.dump(data, fp)


def generate_sha(input_string):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode("utf-8"))
    return sha256_hash.hexdigest()


def readability_stopping(readability, target):
    for key in readability:
        if readability[key] > target[key]:
            return readability_operators[key], {key: readability[key]}
    return [], None


def color_print_line(line):
    return f"{TextColor.HEADER}{line}{TextColor.ENDC}"


def tokenize_code(code):
    tokens = word_tokenize(code)
    return tokens


def clear_string(old_string):
    lines = old_string.splitlines()
    stripped_lines = [line.rstrip() for line in lines]
    cleaned_string = "\n".join(stripped_lines)
    return cleaned_string


def write_header_csv(csv_path, fields):
    print(csv_path)
    with open(csv_path, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()


def write_dict_csv(csv_path, fields, dict_data):
    with open(csv_path, "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writerow(dict_data)


def create_import(name, asname):
    ImportNode = ast.Import(names=[ast.alias(name=name, asname=asname)])
    return ImportNode


def create_importFrom(module, name, asname, level):
    ImportFromNode = ast.ImportFrom(
        module=module, names=[ast.alias(name=name, asname=asname)], level=level
    )
    return ImportFromNode


def get_imports(root):
    import_nodes = []
    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Import):
            if node not in import_nodes:
                import_nodes.append(node)
        elif isinstance(node, ast.ImportFrom):
            if node not in import_nodes:
                import_nodes.append(node)
    return import_nodes


def read_file(file_path):
    file = open(file_path, "r")
    content = file.read()
    return content


def write_file(file_path, content):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    except:
        pass
    f = open(file_path, "w")
    f.write(content)
    f.close()


def write_json(file_path, dict):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    except:
        pass
    with open(file_path, "w") as fp:
        json.dump(dict, fp, indent=4)


def git_diff(file_path):
    diff_path = file_path.replace(".py", "_diff.patch")
    diff_opts = ["git", "diff", file_path]  # , "|& tee", diff_path
    print(" ".join(diff_opts), flush=True)
    diff = subprocess.run(diff_opts, stdout=subprocess.PIPE)
    diff_output = diff.stdout.decode("utf-8")
    write_file(diff_path, diff_output)
    return diff_path


def diff(source_file, target_file):
    diff_path = target_file.replace(".py", "_diff.patch")
    diff_opts = ["diff", "-u", source_file, target_file]
    diff_output = run_cmds(diff_opts, None)
    write_file(diff_path, diff_output)
    return diff_output, diff_path


def get_python_files_dir(directory):
    print(directory)
    file_list = []
    for dir, _, files in os.walk(directory):
        for file in files:
            if (".py") in file:
                file_path = os.path.join(dir, file)
                file_list.append(file_path)
    return file_list
