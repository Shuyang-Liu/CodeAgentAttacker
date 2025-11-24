import ast


class RemoveTryExcept(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def visit_Try(self, node):
        if self.counter >= self.maxnum:
            return node
        self.modified = True
        self.counter += 1
        # replace try-except block with the body of the try block
        return [self.visit(stmt) for stmt in node.body]


def apr_remove_try_except(python_code, applicable_rules):
    root = ast.parse(python_code)
    transformer = RemoveTryExcept()
    new_root = transformer.visit(root)
    ast.fix_missing_locations(new_root)
    if transformer.modified:
        applicable_rules.append("apr_remove_try_except")
    update_content = ast.unparse(new_root)
    return update_content, applicable_rules


def init(python_code, applicable_rules):
    update_content, applicable_rules = apr_remove_try_except(
        python_code, applicable_rules
    )
    return update_content, applicable_rules
