"""Large stress-test demo: 60 teachers, 240 theory + 120 lab sessions/week.

Structure, chosen to hit the requested counts *exactly*:

- 10 departments x 6 semesters = 60 unique (department, semester) cells.
- Each cell owns exactly one class group and exactly one "home" teacher, so
  a teacher's courses (matched to their own department+semester) are only
  ever taken by their own group -- no accidental multi-section fan-out.
- Each teacher explicitly teaches 4 theory courses (1 session/week each) and
  2 lab courses (1 session/week each, 2 slots long) -> 60*4=240 theory
  sessions, 60*2=120 lab sessions, 360 total, matching the brief precisely.
- 40 teachers have a FRI+SAT weekend (unavailable both days, all slots); the
  remaining 20 have a THU+FRI weekend.
- Timeslots are split into a fixed theory pool (slots 1-6, LECTURE/TUTORIAL
  only) and a fixed lab pool (slots 7-10, two 2-slot LAB blocks/day) via
  TimeSlot.session_type_scope (H15) -- "fixed timeslots for lab vs theory".
- Room counts are parameters so the caller can search for the tightest
  feasible values ("just enough to push the limit").
"""

from __future__ import annotations

import pandas as pd

DAYS = ["SAT", "SUN", "MON", "TUE", "WED", "THU", "FRI"]
THEORY_SLOTS = [1, 2, 3, 4, 5, 6]
LAB_SLOTS = [7, 8, 9, 10]  # two 2-slot blocks: (7,8) and (9,10)
SLOTS_PER_DAY = 10
N_DEPARTMENTS = 10
SEMESTERS_PER_DEPARTMENT = 6
N_TEACHERS = N_DEPARTMENTS * SEMESTERS_PER_DEPARTMENT  # 60
N_FRI_SAT_WEEKEND = 40
GROUP_SIZE = 45
ROOM_CAPACITY = 50


def _slot_time(index: int):
    start_hour = 8 + index
    return f"{start_hour:02d}:00", f"{start_hour:02d}:50"


def build_stress_frames(n_theory_rooms: int, n_lab_rooms: int) -> dict:
    universities = [{"code": "SU", "name": "Stress-Test University"}]
    buildings = [
        {"code": "TB", "name": "Theory Block", "university_code": "SU"},
        {"code": "LB", "name": "Lab Block", "university_code": "SU"},
    ]
    room_types = [
        {"code": "LECTURE", "name": "Lecture room"},
        {"code": "LAB", "name": "Computer lab"},
    ]

    rooms = [
        {"code": f"TH{i:02d}", "name": f"Theory room {i}", "building_code": "TB",
         "room_type_code": "LECTURE", "capacity": ROOM_CAPACITY}
        for i in range(1, n_theory_rooms + 1)
    ] + [
        {"code": f"LB{i:02d}", "name": f"Lab room {i}", "building_code": "LB",
         "room_type_code": "LAB", "capacity": ROOM_CAPACITY}
        for i in range(1, n_lab_rooms + 1)
    ]

    time_slots = []
    for day in DAYS:
        for index in range(1, SLOTS_PER_DAY + 1):
            start, end = _slot_time(index)
            scope = "LECTURE,TUTORIAL" if index in THEORY_SLOTS else "LAB"
            time_slots.append({
                "day_of_week": day, "slot_index": index,
                "start_time": start, "end_time": end, "is_break": False,
                "session_type_scope": scope,
            })

    departments = [
        {"code": f"D{d:02d}", "name": f"Department {d}", "university_code": "SU"}
        for d in range(N_DEPARTMENTS)
    ]

    cells = [
        (d, semester)
        for d in range(N_DEPARTMENTS)
        for semester in range(1, SEMESTERS_PER_DEPARTMENT + 1)
    ]
    assert len(cells) == N_TEACHERS

    teachers, class_groups, courses, course_session_types, availability, preferences = (
        [], [], [], [], [], []
    )
    for t_idx, (dept_idx, semester) in enumerate(cells):
        dept_code = f"D{dept_idx:02d}"
        teacher_code = f"T{t_idx:02d}"
        weekend = ("FRI", "SAT") if t_idx < N_FRI_SAT_WEEKEND else ("THU", "FRI")
        teachers.append({
            "code": teacher_code, "name": f"Teacher {t_idx:02d}", "department_code": dept_code,
            "max_sessions_per_day": 6, "max_sessions_per_week": 20,
            "employment_type": "FULL_TIME", "prefers_back_to_back": "",
        })
        for day in weekend:
            for index in range(1, SLOTS_PER_DAY + 1):
                availability.append({
                    "teacher_code": teacher_code, "day_of_week": day,
                    "slot_index": index, "availability": "UNAVAILABLE",
                })

        group_code = f"{dept_code}S{semester}"
        class_groups.append({
            "code": group_code, "name": f"{dept_code} semester {semester}",
            "department_code": dept_code, "semester": semester, "size": GROUP_SIZE,
        })

        for n in range(1, 5):
            code = f"{teacher_code}TH{n}"
            courses.append({
                "code": code, "title": f"Theory course {code}", "department_code": dept_code,
                "semester": semester, "credit_hours": 3.0,
                "is_difficult": n == 1, "teacher_code": teacher_code,
            })
            course_session_types.append({
                "course_code": code, "session_type": "LECTURE",
                "sessions_per_week": 1, "duration_slots": 1,
                "required_room_type_code": "LECTURE",
            })
            preferences.append({"teacher_code": teacher_code, "course_code": code, "preference": 5})
        for n in range(1, 3):
            code = f"{teacher_code}LB{n}"
            courses.append({
                "code": code, "title": f"Lab course {code}", "department_code": dept_code,
                "semester": semester, "credit_hours": 1.5,
                "is_difficult": False, "teacher_code": teacher_code,
            })
            course_session_types.append({
                "course_code": code, "session_type": "LAB",
                "sessions_per_week": 1, "duration_slots": 2,
                "required_room_type_code": "LAB",
            })
            preferences.append({"teacher_code": teacher_code, "course_code": code, "preference": 5})

    return {
        "Universities": pd.DataFrame(universities),
        "Departments": pd.DataFrame(departments),
        "Buildings": pd.DataFrame(buildings),
        "RoomTypes": pd.DataFrame(room_types),
        "Rooms": pd.DataFrame(rooms),
        "TimeSlots": pd.DataFrame(time_slots),
        "Teachers": pd.DataFrame(teachers),
        "Courses": pd.DataFrame(courses),
        "CourseSessionTypes": pd.DataFrame(course_session_types),
        "ClassGroups": pd.DataFrame(class_groups),
        "TeacherAvailability": pd.DataFrame(availability),
        "TeacherCoursePreference": pd.DataFrame(preferences),
    }


def write_stress_workbook(path, n_theory_rooms: int, n_lab_rooms: int) -> None:
    frames = build_stress_frames(n_theory_rooms, n_lab_rooms)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet, df in frames.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
