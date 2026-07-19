from app.solver.constraints.base import SoftConstraint


class BuildingTravel(SoftConstraint):
    key = "S14_building_travel"
    description = "Penalise back-to-back group sessions in different buildings."

    def raw_penalty(self, problem, timetable):
        # group -> day -> list of (start_index, end_index, building_id)
        spans = {}
        for session_id, placement in timetable.placements.items():
            s = problem.sessions[session_id]
            building = problem.rooms[placement.room_id].building_id
            spans.setdefault(s.group_id, {}).setdefault(placement.day, []).append(
                (placement.index, placement.index + s.duration - 1, building)
            )
        penalty = 0
        for day_map in spans.values():
            for items in day_map.values():
                items.sort()
                for (_, end_a, bld_a), (start_b, _, bld_b) in zip(items, items[1:]):
                    if start_b == end_a + 1 and bld_a != bld_b:
                        penalty += 1
        return float(penalty)
