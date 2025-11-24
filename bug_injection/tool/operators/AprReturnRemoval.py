import ast
import random


class RemoveOneReturnWithIf(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.return_nodes = []
        self.target_return = None
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def visit_Return(self, node):
        self.return_nodes.append(node)
        return self.generic_visit(node)

    def prepare(self, tree):
        self.visit(tree)
        if not self.return_nodes:
            return False
        self.target_return = random.choice(self.return_nodes)
        return True

    def apply(self, tree):
        if not self.prepare(tree):
            return tree
        return ast.fix_missing_locations(self._remove(tree))

    def _remove(self, node):
        if self.counter >= self.maxnum:
            return node
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, ast.AST):
                        # remove if-stmt containing the return
                        if self._contains_target(item):
                            if isinstance(item, ast.If):
                                self.modified = True
                                self.counter += 1
                                continue  # remove entire if
                        result = self._remove(item)
                        if result is not None:
                            new_list.append(result)
                    else:
                        new_list.append(item)
                setattr(node, field, new_list)
            elif isinstance(value, ast.AST):
                if self._contains_target(value) and isinstance(value, ast.If):
                    self.modified = True
                    self.counter += 1
                    setattr(node, field, None)
                else:
                    setattr(node, field, self._remove(value))
        return self._remove_target_if_match(node)

    def _contains_target(self, node):
        # returns True if target return is inside the node subtree
        for sub in ast.walk(node):
            if sub is self.target_return:
                return True
        return False

    def _remove_target_if_match(self, node):
        if node is self.target_return:
            self.modified = True
            return None
        return node


def apr_remove_one_return(python_code, applicable_rules):
    tree = ast.parse(python_code)
    transformer = RemoveOneReturnWithIf()
    new_tree = transformer.apply(tree)
    if transformer.modified:
        applicable_rules.append("apr_return_removal")
    return ast.unparse(new_tree), applicable_rules


def init(python_code, applicable_rules):
    return apr_remove_one_return(python_code, applicable_rules)
