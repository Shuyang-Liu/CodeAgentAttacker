# Bug Injection Analysis Report

## Summary

### 2. Observation Content Types
Agent trajectories contain two types of observations:
- **Python code** (from commands like `cat file.py`, `grep pattern file.py`) → Uses **AST operators**
- **Shell output** (from commands like `ls`, `find`, `echo`) → Uses **text_perturbation**

### 3. Automatic Strategy Selection
The `inject_bugs()` function automatically:
- Tries to parse content as Python (`ast.parse()`)
- If successful → applies AST-based mutation operators
- If failed → applies text-based perturbations

## Evidence

### Test Results

#### AST Operators on Python Code:
```
Seed 101: ['apr_change_return']
Original:    return _separable(transform._submodels[0])
Transformed: return not _separable(transform._submodels[0])
✓ Successfully mutated Python code
```

#### Text Perturbation on Shell Output:
```
Seed 202: ['text_perturbation']
Original:    total 672\ndrwxrwxrwx  1 root root...
Transformed: (lines deleted/reordered/noise added)
✓ Successfully perturbed text output
```

### Operator Application Rates

From testing with seeds 42-56 (15 iterations):
- **Applied**: 7 times (47%) - AST operators worked
- **Skipped**: 8 times (53%) - Hit the 50% skip threshold

**Available AST Operators:**
- `apr_change_arith_op` - Change arithmetic operators (+, -, *, /)
- `apr_change_compare_op` - Change comparison operators (<, >, ==, !=)
- `apr_change_condition_op` - Change logical operators (and, or)
- `apr_change_type` - Change variable types
- `apr_change_return` - Mutate return statements
- `apr_remove_try_except` - Remove exception handling
- `apr_remove_if_condition` - Remove if conditions
- `apr_loop_unwrap` - Unwrap loops
- And 7 more...

## Observations from Trajectory Analysis

From analyzing `astropy__astropy-12907.traj.json`:

| Obs # | Type   | Command Type | Parseable as Python |
|-------|--------|--------------|---------------------|
| 1     | Text   | ls -la       | ✗                   |
| 2     | Text   | grep         | ✗                   |
| 3     | Python | cat file.py  | ✓                   |
| 4     | Text   | grep -A      | ✗                   |
| 5     | Python | cat file.py  | ✓                   |
| 7     | Python | cat file.py  | ✓                   |
| 8     | Python | cat file.py  | ✓                   |
| 9     | Python | cat file.py  | ✓                   |

**Result**: ~40-50% of observations contain valid Python code and can use AST operators.

## Current Implementation is Correct

The current implementation in `/bug_injection/simulator/run_mini_simulator.py`:

✓ Correctly loads trajectories
✓ Correctly extracts actions and observations
✓ Correctly applies bug injection
✓ Automatically selects appropriate mutation strategy
✓ Handles both Python and text content

## Why You See "None" Operators

When running the simulator, you'll see:
- `Applied Operators: None` - The 50% skip was triggered
- `Applied Operators: []` - No applicable operators found
- `Applied Operators: ['text_perturbation']` - Text perturbation applied
- `Applied Operators: ['apr_change_compare_op', ...]` - AST operators applied

## Recommendations

### Option 1: Keep Current Behavior (Recommended for Realism)
The 50% skip simulates realistic scenarios where not every observation is attacked.

### Option 2: Force Injection (For Testing)
Remove the 50% skip in `bug_injector.py` line 160:
```python
# Comment out or remove:
# if random.random() < 0.5:
#     return source_code, []
```

### Option 3: Increase Injection Rate
Change line 160 to lower probability:
```python
if random.random() < 0.2:  # Only skip 20% of the time
    return source_code, []
```

## Verification

Run the simulator with verbose mode to see detailed operator information:

```bash
conda activate attacker
python bug_injection/simulator/run_mini_simulator.py \
    mini-swe-agent/outputs/swebench/devstral-small/astropy__astropy-12907/astropy__astropy-12907.traj.json \
    --verbose --seed 42
```

Look for steps where Python code is in the observation (from `cat` commands) - these will show AST operators being applied.
