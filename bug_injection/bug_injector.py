"""
API for injecting bugs into agent observation.

This module provides a simple interface to transform Python code by randomly
applying mutation operators that introduce subtle bugs. For non-Python text,
it applies text-based perturbations.
"""

import ast
import random
from typing import List, Tuple, Optional

from .tool import python_transformer, text_transformer


class BugInjector:
    """Transform Python code by applying random mutation operators."""

    _OPERATOR_MAP = {
        "apr_change_arith_op": python_transformer.apr_change_arith_op,
        "apr_change_compare_op": python_transformer.apr_change_compare_op,
        "apr_change_condition_op": python_transformer.apr_change_condition_op,
        "apr_change_return": python_transformer.apr_change_return,
        "apr_change_type": python_transformer.apr_change_type,
        "apr_remove_try_except": python_transformer.apr_remove_try_except,
        "apr_remove_if_condition": python_transformer.apr_remove_if_condition,
        "apr_remove_if_chunk": python_transformer.apr_remove_if_chunk,
        "apr_remove_null_check_condition": python_transformer.apr_remove_null_check_condition,
        "apr_remove_partial_condition": python_transformer.apr_remove_partial_condition,
        "apr_add_random_exp_in_condition": python_transformer.apr_add_random_exp_in_condition,
        "apr_loop_unwrap": python_transformer.apr_loop_unwrap,
        "apr_replace_single_var_usage": python_transformer.apr_replace_single_var_usage,
        "apr_method_call_replacement": python_transformer.apr_method_call_replacement,
        "apr_else_removal": python_transformer.apr_else_removal,
        "apr_method_call_para_replacement": python_transformer.apr_method_call_para_replacement,
    }

    def __init__(self, max_operators: int = 3, seed: Optional[int] = None):
        """
        Initialize the bug injector.

        Args:
            max_operators: Maximum number of operators to apply (1-3)
            seed: Random seed for reproducibility (optional)
        """
        self.max_operators = min(max(1, max_operators), 3)
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def transform(self, source_code: str) -> Tuple[str, List[str]]:
        """
        Transform source code by applying random mutation operators.

        Uses AST-based transformation for valid Python code,
        falls back to text-based perturbation for unparseable input.

        Args:
            source_code: The original Python source code to transform

        Returns:
            Tuple of (transformed_code, applied_operators)
        """
        # Try AST-based transformation first
        if self._is_parseable(source_code):
            return self._transform_with_ast(source_code)

        # Fall back to text-based perturbation
        return self._transform_with_text(source_code)

    def _is_parseable(self, source_code: str) -> bool:
        """Check if code can be parsed as valid Python."""
        try:
            ast.parse(source_code)
            return True
        except SyntaxError:
            return False

    def _transform_with_ast(self, source_code: str) -> Tuple[str, List[str]]:
        """Transform valid Python code using AST-based operators."""
        normalized_code = self._normalize_code(source_code)
        applicable_operators = self._find_applicable_operators(normalized_code)

        if not applicable_operators:
            return normalized_code, []

        # Randomly select 1 to max_operators
        num_operators = random.randint(1, min(self.max_operators, len(applicable_operators)))
        selected_operators = random.sample(applicable_operators, num_operators)

        # Apply operators sequentially
        transformed_code = normalized_code
        applied_operators = []

        for operator in selected_operators:
            try:
                transformed_code, applied_operators = self._OPERATOR_MAP[operator](
                    transformed_code, applied_operators
                )
            except Exception:
                continue

        return transformed_code, applied_operators

    def _transform_with_text(self, source_code: str) -> Tuple[str, List[str]]:
        """Transform unparseable text using text-based perturbation."""
        transformed = text_transformer.transform_non_code_text(
            source_code,
            seed=self.seed
        )
        return transformed, ["text_perturbation"]

    @staticmethod
    def _normalize_code(source_code: str) -> str:
        """Normalize code via AST parse/unparse for consistent formatting."""
        lines = source_code.splitlines()
        stripped_lines = [line.rstrip() for line in lines]
        cleaned_code = "\n".join(stripped_lines)

        tree = ast.parse(cleaned_code)
        return ast.unparse(tree)

    def _find_applicable_operators(self, source_code: str) -> List[str]:
        """Find all operators that can be applied to the given source code."""
        applicable_operators = []

        for operator, func in self._OPERATOR_MAP.items():
            try:
                _, test_applicable = func(source_code, [])
                if operator in test_applicable:
                    applicable_operators.append(operator)
            except Exception:
                continue

        return applicable_operators


def inject_bugs(
    source_code: str,
    max_operators: int = 3,
    seed: Optional[int] = None
) -> Tuple[str, List[str]]:
    """
    Inject bugs into Python source code using random mutation operators.

    Args:
        source_code: The original Python source code
        max_operators: Maximum number of operators to apply (1-3)
        seed: Random seed for reproducibility (optional)

    Returns:
        Tuple of (transformed_code, applied_operators)

    Example:
        >>> code = "def add(a, b):\\n    return a + b"
        >>> transformed, operators = inject_bugs(code, max_operators=2)
        >>> print(f"Applied: {operators}")
        >>> print(transformed)
    """
    # randomly decide whether to inject bugs
    if random.random() < 0.3:
        return source_code, []
    return BugInjector(max_operators=max_operators, seed=seed).transform(source_code)
