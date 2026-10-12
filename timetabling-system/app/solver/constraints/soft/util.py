"""Shared helpers for soft constraint penalty computation."""

from typing import Dict, Iterable, List, Set


def day_gaps(indexes: Set[int]) -> int:
    """Idle slots between first and last occupied slot of a day."""
    if len(indexes) < 2:
        return 0
    return (max(indexes) - min(indexes) + 1) - len(indexes)


def consecutive_runs(indexes: Set[int]) -> List[int]:
    """Lengths of maximal consecutive runs in a set of slot indexes."""
    runs, run = [], 0
    prev = None
    for i in sorted(indexes):
        if prev is not None and i == prev + 1:
            run += 1
        else:
            if run:
                runs.append(run)
            run = 1
        prev = i
    if run:
        runs.append(run)
    return runs


def excess_over_max_run(indexes: Set[int], max_run: int) -> int:
    return sum(max(0, r - max_run) for r in consecutive_runs(indexes))


def total_slots(day_sets: Dict[str, Set[int]]) -> int:
    return sum(len(s) for s in day_sets.values())


def active_days(day_sets: Dict[str, Set[int]]) -> List[str]:
    return [d for d, s in day_sets.items() if s]
