import ast
import random


class RemoveRandomIf(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.if_nodes = []
        self.target = None
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def visit_If(self, node):
        self.if_nodes.append(node)
        self.generic_visit(node)
        return node

    def mark_target(self, root):
        self.visit(root)
        if self.if_nodes and self.counter < self.maxnum:
            self.target = random.choice(self.if_nodes)
            self.modified = True
            self.counter += 1

    def remove_target(self, node):
        if node is self.target:
            # remove the if-block entirely; replace with body or pass
            return node.body if node.body else [ast.Pass()]
        return self.generic_visit(node)

    def transform(self, root):
        return self._transform_node(root)

    def _transform_node(self, node):
        if isinstance(node, list):
            return [self._transform_node(n) for n in node]
        elif isinstance(node, ast.If):
            return self.remove_target(node)
        else:
            for field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    setattr(node, field, [self._transform_node(v) for v in value])
                elif isinstance(value, ast.AST):
                    setattr(node, field, self._transform_node(value))
            return node


def apr_remove_random_if(python_code, applicable_rules):
    root = ast.parse(python_code)
    transformer = RemoveRandomIf()
    transformer.mark_target(root)

    if transformer.modified:
        new_root = transformer.transform(root)
        ast.fix_missing_locations(new_root)
        applicable_rules.append("apr_remove_if_condition")
        update_content = ast.unparse(new_root)
        return update_content, applicable_rules
    else:
        return python_code, applicable_rules


def init(python_code, applicable_rules):
    update_content, applicable_rules = apr_remove_random_if(
        python_code, applicable_rules
    )
    return update_content, applicable_rules
