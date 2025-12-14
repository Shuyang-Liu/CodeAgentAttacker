"""
Bug Injection Toolkit

A clean API for injecting bugs into Python source code using various mutation operators.
"""

from .bug_injector import BugInjector, inject_bugs

__all__ = ["BugInjector", "inject_bugs"]
__version__ = "0.1.0"
