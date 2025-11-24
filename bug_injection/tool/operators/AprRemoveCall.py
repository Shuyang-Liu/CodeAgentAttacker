import ast


class RemoveCallKeepArg(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def visit_Call(self, node):
        self.generic_visit(node)  # args first
        if self.counter >= self.maxnum:
            return node

        # only transform simple calls with exactly one positional argument
        if len(node.args) == 1 and isinstance(node.args[0], ast.expr):
            self.modified = True
            self.counter += 1
            return node.args[0]  # replace entire call with its argument

        return node


def apr_remove_call_keep_arg(python_code, applicable_rules):
    tree = ast.parse(python_code)
    transformer = RemoveCallKeepArg()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)

    if transformer.modified:
        applicable_rules.append("apr_remove_call")
    return ast.unparse(new_tree), applicable_rules


def init(python_code, applicable_rules):
    return apr_remove_call_keep_arg(python_code, applicable_rules)
