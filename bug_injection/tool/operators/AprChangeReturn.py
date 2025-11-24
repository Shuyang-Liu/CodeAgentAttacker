import ast


class ChangeReturn(ast.NodeTransformer):
    def __init__(self, maxnum):
        super().__init__()
        self.counter = 0
        self.maxnum = maxnum

    def visit_Return(self, node: ast.Return):
        self.generic_visit(node)

        if node.value is None:
            return node

        if self.counter >= self.maxnum:
            return node

        if (
            isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, (int, float, complex))
            and not isinstance(node.value.value, bool)
        ):
            new_const = ast.Constant(value=-node.value.value + 10)
            node.value = ast.copy_location(new_const, node.value)
            self.counter += 1
            return node

        new_unary = ast.UnaryOp(op=ast.Not(), operand=node.value)
        node.value = ast.copy_location(new_unary, node.value)
        self.counter += 1
        return node


def apr_change_return(python_code: str, applicable_rules: list, maxnum: int = 3):
    """
    Transform up to `maxnum` return statements in python_code and
    append "apr_change_return" to applicable_rules if any change happened.
    Returns (updated_source, applicable_rules).
    """
    root = ast.parse(python_code)
    transformer = ChangeReturn(maxnum=maxnum)
    new_root = transformer.visit(root)

    # Fill in missing lineno/col_offset attributes so unparse works reliably.
    new_root = ast.fix_missing_locations(new_root)

    try:
        update_content = ast.unparse(new_root)
    except Exception:
        # If ast.unparse fails for some reason, fallback to dumping the tree for debugging.
        update_content = ast.dump(new_root, include_attributes=True)
    if transformer.counter > 0:
        # ensure list exists
        if applicable_rules is None:
            applicable_rules = []
        applicable_rules.append("apr_change_return")
    return update_content, applicable_rules


def init(python_code: str, applicable_rules: list):
    return apr_change_return(python_code, applicable_rules)
