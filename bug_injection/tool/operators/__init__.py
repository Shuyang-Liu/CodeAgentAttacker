"""Mutation operators for bug injection."""

from bug_injection.tool.operators import AprChangeArithOp
from bug_injection.tool.operators import AprChangeCompareOp
from bug_injection.tool.operators import AprChangeConditionOp
from bug_injection.tool.operators import AprChangeReturn
from bug_injection.tool.operators import AprChangeType
from bug_injection.tool.operators import AprExceptionRemoval
from bug_injection.tool.operators import AprIfBlockRemoval
from bug_injection.tool.operators import AprIfChunkRemoval
from bug_injection.tool.operators import AprNullCheckRemoval
from bug_injection.tool.operators import AprPartialConditionRemoval
from bug_injection.tool.operators import AprConditionAddition
from bug_injection.tool.operators import AprLoopUnwrap
from bug_injection.tool.operators import AprVarReplacement
from bug_injection.tool.operators import AprMethodCallReplacement
from bug_injection.tool.operators import AprReturnRemoval
from bug_injection.tool.operators import AprElseRemoval
from bug_injection.tool.operators import AprMethodCallParReplacement
from bug_injection.tool.operators import AprRemoveCall
