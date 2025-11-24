import ast
import random


class RemoveRandomIfCondition(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def visit_If(self, node):
        self.generic_visit(node)  # children first

        if self.counter >= self.maxnum:
            return node

        if isinstance(node.test, ast.BoolOp) and len(node.test.values) > 1:
            # only proceed for 'and' or 'or' with multiple values
            self.modified = True
            self.counter += 1
            values = node.test.values
            index_to_remove = random.randint(0, len(values) - 1)
            new_values = values[:index_to_remove] + values[index_to_remove + 1 :]

            if len(new_values) == 1:
                node.test = new_values[0]  # as a single condition
            else:
                node.test.values = new_values

        return node


def apr_remove_partial_condition(python_code, applicable_rules):
    root = ast.parse(python_code)
    transformer = RemoveRandomIfCondition()
    new_root = transformer.visit(root)
    ast.fix_missing_locations(new_root)
    if transformer.modified:
        applicable_rules.append("apr_remove_partial_condition")
    return ast.unparse(new_root), applicable_rules


def init(python_code, applicable_rules):
    return apr_remove_partial_condition(python_code, applicable_rules)
