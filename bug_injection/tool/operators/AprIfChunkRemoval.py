import ast
import random


class RemoveEntireIf(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.target_if = None
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def find_if_nodes(self, node):
        self.if_nodes = []
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                self.if_nodes.append(child)

    def mark_target(self, root):
        self.find_if_nodes(root)
        if self.if_nodes and self.counter < self.maxnum:
            self.target_if = random.choice(self.if_nodes)
            self.modified = True
            self.counter += 1

    def visit_Module(self, node):
        node.body = self.remove_if_from_body(node.body)
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        node.body = self.remove_if_from_body(node.body)
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        node.body = self.remove_if_from_body(node.body)
        return self.generic_visit(node)

    def visit_For(self, node):
        node.body = self.remove_if_from_body(node.body)
        node.orelse = self.remove_if_from_body(node.orelse)
        return self.generic_visit(node)

    def visit_While(self, node):
        node.body = self.remove_if_from_body(node.body)
        node.orelse = self.remove_if_from_body(node.orelse)
        return self.generic_visit(node)

    def visit_If(self, node):
        node.body = self.remove_if_from_body(node.body)
        node.orelse = self.remove_if_from_body(node.orelse)
        return self.generic_visit(node)

    def remove_if_from_body(self, body):
        if not body:
            return body
        new_body = []
        for stmt in body:
            if stmt is self.target_if:
                continue  # skip this if-statement entirely
            new_body.append(stmt)
        return new_body


def apr_remove_if_chunk(python_code, applicable_rules):
    root = ast.parse(python_code)
    transformer = RemoveEntireIf()
    transformer.mark_target(root)
    if transformer.modified:
        new_root = transformer.visit(root)
        ast.fix_missing_locations(new_root)
        applicable_rules.append("apr_remove_if_chunk")
        update_content = ast.unparse(new_root)
        return update_content, applicable_rules
    else:
        return python_code, applicable_rules


def init(python_code, applicable_rules):
    update_content, applicable_rules = apr_remove_if_chunk(
        python_code, applicable_rules
    )
    return update_content, applicable_rules
