import ast
import random


class AddExtraCheckWithExistingVar(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.modified = False
        self.if_nodes = []
        self.maxnum = maxnum
        self.counter = 0

    def visit_If(self, node):
        self.generic_visit(node)
        self.if_nodes.append(node)
        return node

    def extract_vars(self, node):
        vars = set()
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Name) and isinstance(subnode.ctx, ast.Load):
                vars.add(subnode.id)
        return list(vars)

    def make_random_expr(self, var_name):
        ops = [ast.NotEq(), ast.Gt(), ast.Lt()]
        op = random.choice(ops)
        value = ast.Constant(value=random.randint(1, 100))
        return ast.Compare(
            left=ast.Name(id=var_name, ctx=ast.Load()), ops=[op], comparators=[value]
        )

    def apply(self, tree):
        if self.counter >= self.maxnum:
            return tree

        self.visit(tree)
        if not self.if_nodes:
            return tree

        target_if = random.choice(self.if_nodes)
        var_candidates = self.extract_vars(target_if.test)

        if not var_candidates:
            return tree  # no usable var, skip

        chosen_var = random.choice(var_candidates)
        new_expr = self.make_random_expr(chosen_var)

        if isinstance(target_if.test, ast.BoolOp) and isinstance(
            target_if.test.op, ast.And
        ):
            target_if.test.values.append(new_expr)
        else:
            target_if.test = ast.BoolOp(op=ast.And(), values=[target_if.test, new_expr])

        self.modified = True
        self.counter += 1
        return tree


def apr_add_random_exp_in_condition(python_code, applicable_rules):
    tree = ast.parse(python_code)
    transformer = AddExtraCheckWithExistingVar()
    new_tree = transformer.apply(tree)
    ast.fix_missing_locations(new_tree)
    if transformer.modified:
        applicable_rules.append("apr_add_random_exp_in_condition")
    return ast.unparse(new_tree), applicable_rules


def init(python_code, applicable_rules):
    return apr_add_random_exp_in_condition(python_code, applicable_rules)
