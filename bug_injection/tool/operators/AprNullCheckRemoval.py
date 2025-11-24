import ast


class RemoveNullCheckCondition(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def visit_If(self, node):
        self.generic_visit(node)  # recursively process nested statements
        # print(ast.unparse(node))
        # handle `if x == None`, `if x != None`, `if x is None`, `if x is not None`
        if isinstance(node.test, ast.Compare) and self.counter < self.maxnum:
            if (
                len(node.test.comparators) == 1
                and isinstance(node.test.comparators[0], ast.Constant)
                and node.test.comparators[0].value is None
                and isinstance(node.test.ops[0], (ast.Is, ast.IsNot, ast.Eq, ast.NotEq))
            ):
                self.modified = True
                self.counter += 1
                return node.body  # Promote body to parent

        return node

    def visit_Module(self, node):
        node.body = self._flatten(node.body)
        return node

    def visit_FunctionDef(self, node):
        node.body = self._flatten(node.body)
        return node

    def _flatten(self, stmts):
        new_body = []
        for stmt in stmts:
            result = self.visit(stmt)
            if isinstance(result, list):
                new_body.extend(result)
            else:
                new_body.append(result)
        return new_body


def apr_remove_null_check_condition(python_code, applicable_rules):
    tree = ast.parse(python_code)
    transformer = RemoveNullCheckCondition()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    if transformer.modified:
        applicable_rules.append("apr_remove_null_check_condition")
    return ast.unparse(new_tree), applicable_rules


def init(python_code, applicable_rules):
    return apr_remove_null_check_condition(python_code, applicable_rules)
