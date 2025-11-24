import ast
import random
import builtins


class ReplaceSingleCallName(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.call_nodes = []
        self.modified = False
        self.target_node = None
        self.replacement_func_name = None
        self.builtins = set(dir(builtins))
        self.defined_funcs = set()
        self.maxnum = maxnum
        self.counter = 0

    def visit_FunctionDef(self, node):
        self.defined_funcs.add(node.name)
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        if isinstance(node.func, (ast.Name, ast.Attribute)):
            func_name = self._get_func_name(node.func)
            if func_name and func_name not in self.builtins:
                self.call_nodes.append(node)
        self.generic_visit(node)
        return node

    def _get_func_name(self, func):
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return func.attr
        return None

    def prepare(self, tree):
        self.visit(tree)

        if not self.call_nodes or len(self.defined_funcs) < 2:
            return False

        self.target_node = random.choice(self.call_nodes)
        original_name = self._get_func_name(self.target_node.func)

        replacement_candidates = list(self.defined_funcs - {original_name})
        if not replacement_candidates:
            return False

        self.replacement_func_name = random.choice(replacement_candidates)
        return True

    def transform(self, node):
        if node is self.target_node and self.counter < self.maxnum:
            self.modified = True
            self.counter += 1
            if isinstance(node.func, ast.Name):
                node.func.id = self.replacement_func_name
            elif isinstance(node.func, ast.Attribute):
                node.func.attr = self.replacement_func_name
        return self.generic_visit(node)

    def apply(self, tree):
        if not self.prepare(tree):
            return tree
        return ast.fix_missing_locations(self._transform_ast(tree))

    def _transform_ast(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, ast.AST):
                        new_list.append(self._transform_ast(item))
                    else:
                        new_list.append(item)
                setattr(node, field, new_list)
            elif isinstance(value, ast.AST):
                setattr(node, field, self._transform_ast(value))
        return self.transform(node)


def apr_replace_single_call_name(python_code, applicable_rules):
    tree = ast.parse(python_code)
    transformer = ReplaceSingleCallName()
    new_tree = transformer.apply(tree)
    if transformer.modified:
        applicable_rules.append("apr_method_call_replacement")
    return ast.unparse(new_tree), applicable_rules


def init(python_code, applicable_rules):
    return apr_replace_single_call_name(python_code, applicable_rules)
