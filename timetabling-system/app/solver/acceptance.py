"""Pluggable acceptance criteria for Phase 2 (design doc section 4)."""

from __future__ import annotations

from abc import ABC, abstractmethod


class AcceptanceCriterion(ABC):
    @abstractmethod
    def accept(self, candidate_cost: float, current_cost: float, rng) -> bool: ...

    def on_accept(self, cost: float) -> None:
        pass


class LateAcceptanceHillClimbing(AcceptanceCriterion):
    """LAHC: accept if candidate beats the cost from `history_length`
    accepted-iterations ago, or the current cost."""

    def __init__(self, history_length: int, initial_cost: float):
        self.history = [initial_cost] * max(1, history_length)
        self.pointer = 0

    def accept(self, candidate_cost, current_cost, rng):
        return candidate_cost <= self.history[self.pointer] or candidate_cost <= current_cost

    def on_accept(self, cost):
        self.history[self.pointer] = cost
        self.pointer = (self.pointer + 1) % len(self.history)


class SimulatedAnnealing(AcceptanceCriterion):
    def __init__(self, initial_temp: float, cooling: float):
        self.temperature = max(initial_temp, 1e-9)
        self.cooling = cooling

    def accept(self, candidate_cost, current_cost, rng):
        import math

        if candidate_cost <= current_cost:
            return True
        delta = candidate_cost - current_cost
        return rng.random() < math.exp(-delta / max(self.temperature, 1e-9))

    def on_accept(self, cost):
        self.temperature *= self.cooling


def build_acceptance(config: dict, initial_cost: float) -> AcceptanceCriterion:
    method = str(config.get("acceptance_method", "lahc")).lower()
    if method == "simulated_annealing":
        return SimulatedAnnealing(
            float(config.get("sa_initial_temp", 10.0)),
            float(config.get("sa_cooling", 0.999)),
        )
    return LateAcceptanceHillClimbing(int(config.get("lahc_history_length", 500)), initial_cost)
