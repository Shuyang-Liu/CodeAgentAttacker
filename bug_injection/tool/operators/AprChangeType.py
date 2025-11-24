import ast
import random


class ChangeType(ast.NodeTransformer):
    def __init__(self, maxnum):
        self.counter = 0
        self.maxnum = maxnum

    def visit_Num(self, node):
        if isinstance(node.n, int) and self.counter < self.maxnum:
            choices = [str(node.n)]
            node.n = random.choice(choices)
            self.counter += 1
        elif isinstance(node.n, float) and self.counter < self.maxnum:
            choices = [str(node.n)]
            node.n = random.choice(choices)
            self.counter += 1
        return self.generic_visit(node)


def apr_change_type(python_code, applicable_rules, maxnum=3):
    root = ast.parse(python_code)
    transformer = ChangeType(maxnum=3)
    new_root = transformer.visit(root)
    if transformer.counter > 0:
        applicable_rules.append("apr_change_type")
    update_content = ast.unparse(new_root)
    return update_content, applicable_rules


def init(python_code, applicable_rules):
    update_content, applicable_rules = apr_change_type(python_code, applicable_rules)
    return update_content, applicable_rules
