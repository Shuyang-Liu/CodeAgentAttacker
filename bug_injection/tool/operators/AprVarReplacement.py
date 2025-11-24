import ast
import random


class ReplaceSingleVarUsage(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.all_vars = set()
        self.name_nodes = []
        self.target_node = None
        self.replacement_name = None
        self.modified = False
        self.maxnum = maxnum
        self.counter = 0

    def visit_Name(self, node):
        self.name_nodes.append(node)
        self.all_vars.add(node.id)
        return self.generic_visit(node)

    def prepare(self, tree):
        self.visit(tree)
        # need at least 2 unique variable names and 1 usage
        if len(self.all_vars) < 2 or not self.name_nodes:
            return False

        self.target_node = random.choice(self.name_nodes)

        # pick a replacement variable name different from the one being replaced
        candidates = list(self.all_vars - {self.target_node.id})
        self.replacement_name = random.choice(candidates)
        return True

    def transform(self, node):
        if self.counter >= self.maxnum:
            return node
        if node is self.target_node:
            self.modified = True
            self.counter += 1
            return ast.copy_location(
                ast.Name(id=self.replacement_name, ctx=node.ctx), node
            )
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


def apr_replace_single_var_usage(python_code, applicable_rules):
    tree = ast.parse(python_code)
    transformer = ReplaceSingleVarUsage()
    new_tree = transformer.apply(tree)
    if transformer.modified:
        applicable_rules.append("apr_replace_single_var_usage")
    return ast.unparse(new_tree), applicable_rules


def init(python_code, applicable_rules):
    return apr_replace_single_var_usage(python_code, applicable_rules)
