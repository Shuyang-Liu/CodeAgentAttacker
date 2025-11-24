import ast
import random


class RemoveRandomLoop(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.loop_nodes = []
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def visit_For(self, node):
        self.loop_nodes.append(node)
        self.generic_visit(node)
        return node

    def visit_While(self, node):
        self.loop_nodes.append(node)
        self.generic_visit(node)
        return node

    def apply(self, tree):
        if self.counter >= self.maxnum:
            return tree
        self.visit(tree)

        if not self.loop_nodes:
            return tree
        # choose one loop to remove
        loop_to_remove = random.choice(self.loop_nodes)
        self.modified = True
        self.counter += 1

        # replace the loop with its body (flatten)
        return self._replace_node(tree, loop_to_remove)

    def _replace_node(self, node, target):
        # Replace the target loop node with its body in compound blocks
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                new_list = []
                for item in value:
                    if item is target:
                        new_list.extend(item.body)
                    else:
                        new_list.append(self._replace_node(item, target))
                setattr(node, field, new_list)
            elif isinstance(value, ast.AST):
                setattr(node, field, self._replace_node(value, target))
        return node


def apr_remove_random_loop(python_code, applicable_rules):
    tree = ast.parse(python_code)
    transformer = RemoveRandomLoop()
    new_tree = transformer.apply(tree)
    ast.fix_missing_locations(new_tree)
    if transformer.modified:
        applicable_rules.append("apr_loop_unwrap")
    return ast.unparse(new_tree), applicable_rules


def init(python_code, applicable_rules):
    return apr_remove_random_loop(python_code, applicable_rules)
