import ast
import random


class ChangeArithOps(ast.NodeTransformer):
    def __init__(self, maxnum):
        self.counter = 0
        self.maxnum = maxnum

    def visit_BinOp(self, node):
        replacements = {
            ast.Add: [ast.Sub, ast.Mult, ast.Div],
            ast.Sub: [ast.Add, ast.Mult, ast.Div],
            ast.Mult: [ast.Add, ast.Sub, ast.Div],
            ast.Div: [ast.Add, ast.Sub, ast.Mult],
        }

        op_class = type(node.op)
        if op_class in replacements and self.counter < self.maxnum:
            node.op = random.choice(replacements[op_class])()
            self.counter += 1

        return self.generic_visit(node)


def apr_change_arith_op(python_code, applicable_rules, maxnum=3):
    root = ast.parse(python_code)
    transformer = ChangeArithOps(maxnum=3)
    new_root = transformer.visit(root)
    if transformer.counter > 0:
        applicable_rules.append("apr_change_arith_op")
    update_content = ast.unparse(new_root)
    return update_content, applicable_rules


def init(python_code, applicable_rules):
    update_content, applicable_rules = apr_change_arith_op(
        python_code, applicable_rules
    )
    return update_content, applicable_rules
