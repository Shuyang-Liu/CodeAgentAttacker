import ast
import random
import builtins


class ReplaceOneCallArgument(ast.NodeTransformer):
    def __init__(self, maxnum=3):
        self.call_nodes = []
        self.var_candidates = set()
        self.func_names = set()
        self.target_call = None
        self.target_arg_index = None
        self.replacement_var = None
        self.modified = False
        self.builtins = set(dir(builtins))
        self.maxnum = maxnum
        self.counter = 0

    def visit_FunctionDef(self, node):
        self.func_names.add(node.name)
        for arg in node.args.args:
            self.var_candidates.add(arg.arg)  # include parameters
        self.generic_visit(node)
        return node

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.var_candidates.add(target.id)
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.var_candidates.add(node.id)
        return self.generic_visit(node)

    def visit_Call(self, node):
        func_name = self._get_func_name(node.func)
        if func_name and func_name not in self.builtins and node.args:
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

        # Keep only real variable names (not functions, not builtins)
        real_vars = self.var_candidates - self.func_names - self.builtins
        if not self.call_nodes or len(real_vars) < 2:
            return False

        self.target_call = random.choice(self.call_nodes)
        self.target_arg_index = random.randrange(len(self.target_call.args))

        current_arg = self.target_call.args[self.target_arg_index]
        current_name = current_arg.id if isinstance(current_arg, ast.Name) else None
        candidates = list(real_vars - {current_name} if current_name else real_vars)

        if not candidates:
            return False

        self.replacement_var = random.choice(candidates)
        return True

    def apply(self, tree):
        if not self.prepare(tree):
            return tree
        return ast.fix_missing_locations(self._transform(tree))

    def _transform(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                setattr(
                    node,
                    field,
                    [
                        self._transform(item) if isinstance(item, ast.AST) else item
                        for item in value
                    ],
                )
            elif isinstance(value, ast.AST):
                setattr(node, field, self._transform(value))
        return self._maybe_replace_arg(node)

    def _maybe_replace_arg(self, node):
        if node is self.target_call and self.counter < self.maxnum:
            node.args[self.target_arg_index] = ast.Name(
                id=self.replacement_var, ctx=ast.Load()
            )
            self.modified = True
            self.counter += 1
        return node


def apr_replace_one_call_arg(python_code, applicable_rules):
    tree = ast.parse(python_code)
    transformer = ReplaceOneCallArgument()
    new_tree = transformer.apply(tree)
    if transformer.modified:
        applicable_rules.append("apr_method_call_para_replacement")
    return ast.unparse(new_tree), applicable_rules


def init(python_code, applicable_rules):
    # change parameters in method call
    return apr_replace_one_call_arg(python_code, applicable_rules)
