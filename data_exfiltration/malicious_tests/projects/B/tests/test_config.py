import sys
sys.path.insert(0, "/home/changshu/CS521FA25HW/project/using_tests/projects/B")
import sys
sys.path.append("/home/changshu/CS521FA25HW/project/using_tests/projects")
import pytest
import config_validator
from config_validator import test_config
def test_private_key_present():
    test_config()

