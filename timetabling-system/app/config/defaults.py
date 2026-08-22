"""Seed defaults for ConstraintWeight and SystemConfig (design doc section 6)."""

# (key, tier, weight, is_hard)
HARD_CONSTRAINT_DEFAULTS = [
    ("H01_room_occupancy", 0, 0.0, True),
    ("H02_teacher_clash", 0, 0.0, True),
    ("H03_group_clash", 0, 0.0, True),
    ("H04_room_capacity", 0, 0.0, True),
    ("H05_room_type_match", 0, 0.0, True),
    ("H06_teacher_availability", 0, 0.0, True),
    ("H07_teacher_qualification", 0, 0.0, True),
    ("H08_session_completeness", 0, 0.0, True),
    ("H09_slot_validity", 0, 0.0, True),
    ("H10_multislot_contiguity", 0, 0.0, True),
    ("H11_teacher_max_daily", 0, 0.0, True),
    ("H12_group_max_daily", 0, 0.0, True),
    ("H13_course_once_per_day", 0, 0.0, True),
    ("H14_locked_session", 0, 0.0, True),
    ("H15_slot_type_scope", 0, 0.0, True),
]

SOFT_CONSTRAINT_DEFAULTS = [
    ("S01_teacher_preferred_slots", 1, 8.0, False),
    ("S02_teacher_course_preference", 1, 8.0, False),
    ("S03_group_gaps", 1, 10.0, False),
    ("S04_teacher_gaps", 2, 5.0, False),
    ("S05_group_compact_days", 2, 4.0, False),
    ("S06_teacher_compact_days", 2, 4.0, False),
    ("S07_course_spread", 1, 6.0, False),
    ("S08_group_max_consecutive", 1, 7.0, False),
    ("S09_teacher_max_consecutive", 1, 7.0, False),
    ("S10_early_slot_avoidance", 3, 2.0, False),
    ("S11_late_slot_avoidance", 3, 2.0, False),
    ("S12_lunch_break", 2, 5.0, False),
    ("S13_room_stability", 3, 3.0, False),
    ("S14_building_travel", 2, 6.0, False),
    ("S15_room_utilization_fit", 3, 2.0, False),
    ("S16_teacher_load_balance", 2, 4.0, False),
    ("S17_group_load_balance", 2, 4.0, False),
    ("S18_difficult_course_morning", 2, 5.0, False),
    ("S19_teacher_back_to_back", 3, 3.0, False),
]

# key -> (value, value_type, description)
SYSTEM_CONFIG_DEFAULTS = {
    "group_max_sessions_per_day": ("6", "int", "H12: max occupied slots per group per day"),
    "max_consecutive_group": ("3", "int", "S08: max consecutive slots for a group"),
    "max_consecutive_teacher": ("3", "int", "S09: max consecutive slots for a teacher"),
    "lunch_start_slot": ("4", "int", "S12: lunch window start slot index"),
    "lunch_end_slot": ("5", "int", "S12: lunch window end slot index"),
    "morning_end_slot": ("3", "int", "S18: last morning slot index"),
    "room_fit_slack_threshold": ("2.0", "float", "S15: capacity/size ratio threshold"),
    "phase1_max_repair_iterations": ("20000", "int", "Phase 1 repair iteration budget"),
    "phase1_tabu_tenure": ("25", "int", "Phase 1 tabu tenure"),
    "phase2_time_budget_seconds": ("60", "float", "Phase 2 wall clock budget"),
    "phase2_iteration_budget": ("200000", "int", "Phase 2 iteration budget"),
    "phase2_finisher_fraction": (
        "0.15", "float",
        "share of the Phase 2 budget reserved for a strict improve-only descent pass",
    ),
    "lahc_history_length": ("500", "int", "LAHC history list length"),
    "acceptance_method": ("lahc", "str", "lahc | simulated_annealing"),
    "sa_initial_temp": ("10.0", "float", "SA initial temperature"),
    "sa_cooling": ("0.999", "float", "SA geometric cooling factor"),
    "ruin_fraction": ("0.1", "float", "share of sessions removed by ruin_recreate"),
    "hyper_heuristic_window": ("100", "int", "move success-rate sliding window"),
    "random_seed": ("42", "int", "solver RNG seed"),
}


def parse_config_value(value: str, value_type: str):
    if value_type == "int":
        return int(value)
    if value_type == "float":
        return float(value)
    if value_type == "bool":
        return str(value).strip().lower() in ("1", "true", "yes", "y")
    return value
