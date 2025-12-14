#!/usr/bin/env python3
"""
Simulator for testing the bug injector.

Reads trajectory files, extracts actions step-by-step, feeds them to the attacker,
and randomly perturb the observation, print the perturbed observation.
"""

from __future__ import annotations
import time
import argparse
from pathlib import Path
from typing import Optional

from bug_injection.simulator.mini_extractor import ActionExtractor
from bug_injection.bug_injector import inject_bugs


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Simulate agent execution with perturbed observations"
    )
    parser.add_argument(
        "trajectory_file",
        type=str,
        help="Path to the trajectory JSON file (e.g., *.traj.json)",
    )
    parser.add_argument(
        "--max-operators",
        type=int,
        default=3,
        help="Maximum number of mutation operators to apply (1-3, default: 3)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (optional)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output including thoughts and applied operators",
    )
    return parser.parse_args()


def main():
    """Main entry point for the simulator."""
    args = parse_args()

    # Validate trajectory file exists
    traj_path = Path(args.trajectory_file)
    if not traj_path.exists():
        print(f"Error: Trajectory file not found: {traj_path}")
        return 1

    # Initialize extractor
    print(f"Loading trajectory: {traj_path}")
    extractor = ActionExtractor(traj_path)
    instance_id = extractor.get_instance_id()
    message_count = extractor.get_message_count()

    print(f"Instance ID: {instance_id}")
    print(f"Total messages: {message_count}")
    print("-" * 80)

    # Track statistics
    stats = {
        'total': 0,
        'ast_applied': 0,
        'text_applied': 0,
        'skipped': 0,
        'python_content': 0
    }

    # Process each action-observation pair
    for event, thought, observation in extractor.extract_actions():
        step_idx = event.step_index
        command = event.command
        stats['total'] += 1

        # Check if observation is parseable Python
        import ast
        is_python = False
        try:
            ast.parse(observation)
            is_python = True
            stats['python_content'] += 1
        except:
            pass

        print(f"\n{'=' * 80}")
        print(f"Step {step_idx} [{'Python' if is_python else 'Text'}]")
        print(f"{'=' * 80}")

        if args.verbose and thought:
            print(f"\nTHOUGHT:\n{thought}")

        print(f"\nCOMMAND:\n{command}")

        print(f"\nORIGINAL OBSERVATION:")
        print(f"{observation[:500]}..." if len(observation) > 500 else observation)

        # Perturb the observation using bug injection
        perturbed_obs, applied_ops = inject_bugs(
            observation,
            max_operators=args.max_operators,
            seed=args.seed
        )

        # Update statistics
        if not applied_ops:
            stats['skipped'] += 1
        elif 'text_perturbation' in applied_ops:
            stats['text_applied'] += 1
        else:
            stats['ast_applied'] += 1

        print(f"\nPERTURBED OBSERVATION:")
        print(f"{perturbed_obs[:500]}..." if len(perturbed_obs) > 500 else perturbed_obs)

        if args.verbose or applied_ops:
            status = "SKIPPED (50% chance)" if not applied_ops else f"APPLIED: {applied_ops}"
            print(f"\nOPERATORS: {status}")

        print("-" * 80)

    # Print summary statistics
    print(f"\n{'=' * 80}")
    print("SUMMARY STATISTICS")
    print(f"{'=' * 80}")
    print(f"Total steps:              {stats['total']}")
    print(f"Python observations:      {stats['python_content']} ({stats['python_content']/stats['total']*100:.1f}%)")
    print(f"Text observations:        {stats['total'] - stats['python_content']} ({(stats['total']-stats['python_content'])/stats['total']*100:.1f}%)")
    print(f"\nPerturbation results:")
    print(f"  AST operators applied:  {stats['ast_applied']} ({stats['ast_applied']/stats['total']*100:.1f}%)")
    print(f"  Text perturbation:      {stats['text_applied']} ({stats['text_applied']/stats['total']*100:.1f}%)")
    print(f"  Skipped (no mutation):  {stats['skipped']} ({stats['skipped']/stats['total']*100:.1f}%)")
    print(f"{'=' * 80}")

    print(f"\nSimulation complete!")
    return 0


if __name__ == "__main__":
    exit(main())
