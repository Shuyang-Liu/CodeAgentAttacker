import random
import numpy as np

from bug_injection.tool import utils
from bug_injection.tool import operators


def apr_change_arith_op(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprChangeArithOp.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_change_compare_op(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprChangeCompareOp.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_change_condition_op(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprChangeConditionOp.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_change_type(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprChangeType.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


# operators.AprExceptionRemoval
def apr_remove_try_except(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprExceptionRemoval.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_change_return(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprChangeReturn.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_remove_if_condition(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprIfBlockRemoval.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_remove_if_chunk(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprIfChunkRemoval.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_remove_null_check_condition(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprNullCheckRemoval.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_remove_partial_condition(python_code, applicable_operators):
    try:
        update_content, applicable_operators = (
            operators.AprPartialConditionRemoval.init(python_code, applicable_operators)
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_add_random_exp_in_condition(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprConditionAddition.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_loop_unwrap(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprLoopUnwrap.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_replace_single_var_usage(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprVarReplacement.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_method_call_replacement(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprMethodCallReplacement.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_return_removal(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprReturnRemoval.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_else_removal(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprElseRemoval.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_method_call_para_replacement(python_code, applicable_operators):
    try:
        update_content, applicable_operators = (
            operators.AprMethodCallParReplacement.init(
                python_code, applicable_operators
            )
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def apr_remove_call(python_code, applicable_operators):
    try:
        update_content, applicable_operators = operators.AprRemoveCall.init(
            python_code, applicable_operators
        )
        return update_content, applicable_operators
    except:
        return python_code, applicable_operators


def get_random(source_file, target_file=None):
    python_code = utils.read_file(source_file)
    applicable_operators = []
    try:
        update_content, applicable_operators = apr_change_arith_op(
            python_code, applicable_operators
        )
        update_content, applicable_operators = apr_change_compare_op(
            python_code, applicable_operators
        )
        update_content, applicable_operators = apr_change_condition_op(
            python_code, applicable_operators
        )
        update_content, applicable_operators = apr_change_type(
            python_code, applicable_operators
        )
        update_content, applicable_operators = apr_change_return(
            python_code, applicable_operators
        )
        update_content, applicable_operators = apr_remove_try_except(
            python_code, applicable_operators
        )
    except:
        pass

    random_seed = np.random.randint(0, 2**32 - 1)
    random.seed(random_seed)
    random_operator = None
    if len(applicable_operators):
        random_operator = random.choice(applicable_operators)
    return random_operator, random_seed


def get_all_apr_operators(source_file, target_file=None):
    python_code = utils.read_file(source_file)
    applicable_operators = []
    update_content, applicable_operators = apr_change_arith_op(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_change_compare_op(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_change_condition_op(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_change_return(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_change_type(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_remove_try_except(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_remove_if_condition(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_remove_if_chunk(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_remove_null_check_condition(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_remove_partial_condition(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_add_random_exp_in_condition(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_loop_unwrap(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_replace_single_var_usage(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_method_call_replacement(
        python_code, applicable_operators
    )
    # update_content, applicable_operators = apr_return_removal(
    #     python_code, applicable_operators
    # )
    update_content, applicable_operators = apr_else_removal(
        python_code, applicable_operators
    )
    update_content, applicable_operators = apr_method_call_para_replacement(
        python_code, applicable_operators
    )
    # update_content, applicable_operators = apr_remove_call(python_code, applicable_operators)

    return applicable_operators


def apply_multiple_operators(source_file, target_file, all_operators):
    update_content = utils.read_file(source_file)
    applicable_operators = []
    print(f"* Specified operators: {all_operators}")
    for operator in all_operators:
        update_content, applicable_operators = transformation_single_operator(
            source_file, operator, applicable_operators, target_file
        )
        utils.write_file(target_file, update_content)
        source_file = target_file
    return update_content, applicable_operators


def initialize(
    source_file, single_operator, target_file, file_id=None, apply_all=False
):
    applicable_operators = []
    update_content = utils.read_file(source_file)
    print(
        f"* Instructions: single_operator - {single_operator}; apply_all - {apply_all}"
    )
    if single_operator and not apply_all:
        update_content, applicable_operators = transformation_single_operator(
            source_file, single_operator, applicable_operators, target_file
        )
    elif apply_all and not single_operator:
        update_content, applicable_operators = transformation_all_applicable_operators(
            source_file, applicable_operators, target_file, file_id
        )
    return update_content, applicable_operators


def transformation_all_applicable_operators(
    source_file, operator, applicable_operators, target_file
):
    applicale_apr_operators = get_all_apr_operators(source_file)
    update_content, applicable_operators = apply_multiple_operators(
        source_file, target_file, applicale_apr_operators
    )
    return update_content, applicable_operators


def transformation_single_operator(
    source_file, operator, applicable_operators, target_file
):
    python_code = utils.read_file(source_file)
    if operator == "apr_change_arith_op":
        update_content, applicable_operators = apr_change_arith_op(
            python_code, applicable_operators
        )
    elif operator == "apr_change_compare_op":
        update_content, applicable_operators = apr_change_compare_op(
            python_code, applicable_operators
        )
    elif operator == "apr_change_condition_op":
        update_content, applicable_operators = apr_change_condition_op(
            python_code, applicable_operators
        )
    elif operator == "apr_change_type":
        update_content, applicable_operators = apr_change_type(
            python_code, applicable_operators
        )
    elif operator == "apr_change_return":
        update_content, applicable_operators = apr_change_return(
            python_code, applicable_operators
        )
    elif operator == "apr_remove_try_except":
        update_content, applicable_operators = apr_remove_try_except(
            python_code, applicable_operators
        )
    elif operator == "apr_remove_if_condition":
        update_content, applicable_operators = apr_remove_if_condition(
            python_code, applicable_operators
        )
    elif operator == "apr_remove_if_chunk":
        update_content, applicable_operators = apr_remove_if_chunk(
            python_code, applicable_operators
        )
    elif operator == "apr_remove_null_check_condition":
        update_content, applicable_operators = apr_remove_null_check_condition(
            python_code, applicable_operators
        )
    elif operator == "apr_remove_partial_condition":
        update_content, applicable_operators = apr_remove_partial_condition(
            python_code, applicable_operators
        )
    elif operator == "apr_add_random_exp_in_condition":
        update_content, applicable_operators = apr_add_random_exp_in_condition(
            python_code, applicable_operators
        )
    elif operator == "apr_loop_unwrap":
        update_content, applicable_operators = apr_loop_unwrap(
            python_code, applicable_operators
        )
    elif operator == "apr_replace_single_var_usage":
        update_content, applicable_operators = apr_replace_single_var_usage(
            python_code, applicable_operators
        )
    elif operator == "apr_method_call_replacement":
        update_content, applicable_operators = apr_method_call_replacement(
            python_code, applicable_operators
        )
    # elif operator == "apr_return_removal":
    #     update_content, applicable_operators = apr_return_removal(
    #         python_code, applicable_operators
    #     )
    elif operator == "apr_else_removal":
        update_content, applicable_operators = apr_else_removal(
            python_code, applicable_operators
        )
    elif operator == "apr_method_call_para_replacement":
        update_content, applicable_operators = apr_method_call_para_replacement(
            python_code, applicable_operators
        )
    # elif operator == "apr_remove_call":
    #     update_content, applicable_operators = apr_remove_call(python_code, applicable_operators)
    else:
        raise ValueError(f"Operator {operator} Not Supported")
    return update_content, applicable_operators
