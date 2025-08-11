from dataclasses import dataclass
from typing import Any, Dict


def get_user_overview(user, category_id=None) -> Dict[str, Any]:
    """Return aggregated LMS stats for the given user.

    The implementation currently provides placeholder values and
    determines the user role based on simple flags. Real aggregation
    logic can be implemented later on top of project models.
    """
    role = "student"
    if getattr(user, "is_staff", False):
        role = "admin"
    elif hasattr(user, "profile") and getattr(user.profile, "is_teacher", False):
        role = "teacher"

    cards = {
        "topics_completed": 0,
        "tasks_available": 0,
        "overall_progress_percent": 0.0,
        "active_categories_count": 0,
    }

    progress_by_category = []

    teacher_block = None
    if role in ("teacher", "admin"):
        teacher_block = {
            "created_courses": 0,
            "active_students": 0,
            "avg_students_progress_percent": 0.0,
        }

    return {
        "role": role,
        "cards": cards,
        "progress_by_category": progress_by_category,
        "teacher_block": teacher_block,
    }
