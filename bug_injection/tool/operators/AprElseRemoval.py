import ast


class RemoveElseButKeepBody(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def visit_If(self, node):
        self.generic_visit(node)

        if node.orelse:
            if self.counter >= self.maxnum:
                return node
            self.modified = True
            # remove the else clause, but keep its body promoted
            parent = node
            body = node.body
            else_body = node.orelse
            node.orelse = []  # clear the else
            self.counter += 1

            return [node] + else_body  # promote else_body right after if-block

        return node

    def apply(self, tree):
        new_tree = self._flatten(tree)
        ast.fix_missing_locations(new_tree)
        return new_tree

    def _flatten(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                flat_list = []
                for item in value:
                    if isinstance(item, ast.AST):
                        transformed = self._flatten(item)
                        if isinstance(transformed, list):
                            flat_list.extend(transformed)
                        else:
                            flat_list.append(transformed)
                    else:
                        flat_list.append(item)
                setattr(node, field, flat_list)
            elif isinstance(value, ast.AST):
                transformed = self._flatten(value)
                setattr(node, field, transformed)
        return self.visit(node)


def apr_remove_else_but_keep_body(python_code, applicable_rules):
    tree = ast.parse(python_code)
    transformer = RemoveElseButKeepBody()
    new_tree = transformer.apply(tree)
    if transformer.modified:
        applicable_rules.append("apr_else_removal")
    return ast.unparse(new_tree), applicable_rules


def init(python_code, applicable_rules):
    return apr_remove_else_but_keep_body(python_code, applicable_rules)
