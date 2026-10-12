"""Synthetic sample dataset generator.

`write_sample_workbook(path)` writes a small feasible dataset (~50 sessions);
`scale` multiplies departments/courses/groups for scale testing.
"""

from __future__ import annotations

import pandas as pd

DAYS = ["MON", "TUE", "WED", "THU", "FRI"]
SLOTS_PER_DAY = 8


def _times(index: int):
    start_hour = 8 + index  # slot 1 -> 09:00
    return f"{start_hour + 1:02d}:00", f"{start_hour + 1:02d}:50"


def build_sample_frames(scale: int = 1) -> dict:
    universities = [{"code": "NU", "name": "North University"}]
    departments, buildings, teachers = [], [], []
    courses, course_session_types, class_groups = [], [], []
    availability, preferences = [], []

    buildings = [
        {"code": "B1", "name": "Academic Building 1", "university_code": "NU"},
        {"code": "B2", "name": "Science Complex", "university_code": "NU"},
    ]
    room_types = [
        {"code": "LECTURE", "name": "Lecture room"},
        {"code": "LAB", "name": "Computer lab"},
    ]

    rooms = []
    for d in range(scale):
        for i in range(1, 5):
            rooms.append({
                "code": f"R{d}{i:02d}", "name": f"Room {d}-{i}", "building_code": "B1",
                "room_type_code": "LECTURE", "capacity": 60,
            })
        for i in range(1, 3):
            rooms.append({
                "code": f"L{d}{i:02d}", "name": f"Lab {d}-{i}", "building_code": "B2",
                "room_type_code": "LAB", "capacity": 50,
            })

    time_slots = []
    for day in DAYS:
        for index in range(1, SLOTS_PER_DAY + 1):
            start, end = _times(index)
            time_slots.append({
                "day_of_week": day, "slot_index": index,
                "start_time": start, "end_time": end, "is_break": False,
                "session_type_scope": "",
            })

    for d in range(scale):
        dept = f"D{d:02d}"
        departments.append({"code": dept, "name": f"Department {d}", "university_code": "NU"})
        dept_teachers = []
        for i in range(1, 9):
            code = f"{dept}T{i:02d}"
            dept_teachers.append(code)
            teachers.append({
                "code": code, "name": f"Teacher {dept}-{i}", "department_code": dept,
                "max_sessions_per_day": 4, "max_sessions_per_week": 18,
                "employment_type": "FULL_TIME", "prefers_back_to_back": "",
            })
        # one teacher partially unavailable, one with declared preferred slots
        for index in range(1, 5):
            availability.append({
                "teacher_code": dept_teachers[0], "day_of_week": "MON",
                "slot_index": index, "availability": "UNAVAILABLE",
            })

        for semester, prefix in ((1, "1"), (3, "3")):
            for group_letter in ("A", "B"):
                class_groups.append({
                    "code": f"{dept}S{prefix}{group_letter}",
                    "name": f"{dept} sem {semester} sec {group_letter}",
                    "department_code": dept, "semester": semester, "size": 45,
                })
            for c in range(1, 6):
                code = f"{dept}C{prefix}{c:02d}"
                teacher = dept_teachers[(c - 1 + (semester // 2) * 4) % len(dept_teachers)]
                courses.append({
                    "code": code, "title": f"Course {code}", "department_code": dept,
                    "semester": semester, "credit_hours": 3.0,
                    "is_difficult": c == 1, "teacher_code": teacher,
                })
                course_session_types.append({
                    "course_code": code, "session_type": "LECTURE",
                    "sessions_per_week": 2, "duration_slots": 1,
                    "required_room_type_code": "LECTURE",
                })
                if c <= 2:
                    course_session_types.append({
                        "course_code": code, "session_type": "LAB",
                        "sessions_per_week": 1, "duration_slots": 2,
                        "required_room_type_code": "LAB",
                    })
                preferences.append({
                    "teacher_code": teacher, "course_code": code, "preference": 5,
                })
                backup = dept_teachers[c % len(dept_teachers)]
                if backup != teacher:
                    preferences.append({
                        "teacher_code": backup, "course_code": code, "preference": 3,
                    })

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


def write_sample_workbook(path, scale: int = 1) -> None:
    frames = build_sample_frames(scale)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet, df in frames.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
