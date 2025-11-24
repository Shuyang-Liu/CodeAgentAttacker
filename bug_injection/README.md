# Bug-Injection

## Setup:
- Python 3.10

## Commands:
- All opeartors are in `tool/operators/`

- To run a specific tansformation with one of the above operator:
```
python3 tool/init.py  --src_file [python_src_file] --target_file [python_target_file] -j [result_json_file] --operator [operator]
```
For example, run `python3 tool/init.py  --src_file example/1.py --target_file example/1_transformation.py -j example/1.json --operator apr_change_return`, you will see the results in JSON file `example/1.json`:
```
{
    "file_id": "1",
    "src_file": "example/1.py",
    "target_file": "example/1_transformation.py",
    "single_operator": "apr_change_return",
    "patch_path": "example/1.patch",
    "applicable_operators": [
        "apr_change_return"
    ],
    "exception": null,
    "total_time": 0.000998,
    "diff_output": "--- example/1.py\n+++ example/1_transformation.py\n@@ -1,4 +1,4 @@\n def modified_length(a, b):\n     changed_length = 10\n     a = b + changed_length\n-    return a\n+    return not a\n",
    "original_code": "def modified_length(a, b):\n    changed_length = 10\n    a = b + changed_length\n    return a",
    "transformed_code": "def modified_length(a, b):\n    changed_length = 10\n    a = b + changed_length\n    return not a"
}
```

You can check `example/1.patch` for the diff:
```diff
--- example/1.py
+++ example/1_transformation.py
@@ -1,4 +1,4 @@
 def modified_length(a, b):
     changed_length = 10
     a = b + changed_length
-    return a
+    return not a
```
Patches are stored in the same directory as your target Python file and retain the same file ID.


- To apply all applicable operators:
```
python3 tool/init.py  --src_file [python_src_file] --target_file [python_target_file] -j [result_json_file] --all
```
Example outputs for the above instance:
```
{
    "file_id": "1",
    "src_file": "example/1.py",
    "target_file": "example/1_transformation.py",
    "single_operator": null,
    "patch_path": "example/1.patch",
    "applicable_operators": [
        "apr_change_arith_op",
        "apr_change_return",
        "apr_change_type",
        "apr_replace_single_var_usage"
    ],
    "exception": null,
    "total_time": 0.003758,
    "diff_output": "--- example/1.py\n+++ example/1_transformation.py\n@@ -1,4 +1,4 @@\n def modified_length(a, b):\n-    changed_length = 10\n-    a = b + changed_length\n-    return a\n+    changed_length = '10'\n+    changed_length = b * changed_length\n+    return not a\n",
    "original_code": "def modified_length(a, b):\n    changed_length = 10\n    a = b + changed_length\n    return a",
    "transformed_code": "def modified_length(a, b):\n    changed_length = '10'\n    changed_length = b * changed_length\n    return not a"
}
```
Patch:
```diff
--- example/1.py
+++ example/1_transformation.py
@@ -1,4 +1,4 @@
 def modified_length(a, b):
-    changed_length = 10
-    a = b + changed_length
-    return a
+    changed_length = '10'
+    a = a * changed_length
+    return not a
```

Note: Existing maximum number of each operators are setting to `3`, you can change it by modifying the optional parameter `maxnum` in each operator.
