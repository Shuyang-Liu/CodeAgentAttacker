# Bug Injection

A toolkit for injecting bugs into agent observation using mutation operators.

## Usage

```python
from bug_injection.bug_injector import inject_bugs

code = """
def add(a, b):
    result = a + b
    return result
"""

# Transform code with 1-3 randomly selected operators
transformed, operators = inject_bugs(code, max_operators=3, seed=42)

print(f"Applied: {operators}")
print(transformed)
```

## Parameters

- `source_code` (str): Python code to transform
- `max_operators` (int): Maximum number of operators to apply (1-3, default: 3)
- `seed` (int, optional): Random seed for reproducibility

## Returns

- `transformed_code` (str): The mutated code
- `applied_operators` (list): Names of operators that were applied

## Available Operators

All operators are in `tool/operators/`:
- `apr_change_arith_op` - Mutate arithmetic operators
- `apr_change_compare_op` - Mutate comparison operators
- `apr_change_condition_op` - Mutate logical operators
- `apr_change_return` - Mutate return statements
- `apr_change_type` - Change variable types
- `apr_remove_try_except` - Remove exception handling
- `apr_remove_if_condition` - Remove if blocks
- And more...
