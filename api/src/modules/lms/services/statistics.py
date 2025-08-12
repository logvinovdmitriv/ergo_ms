"""Utility functions for LMS statistics."""

from dataclasses import dataclass
from typing import Any, Dict, Iterable

from django.db.models import Count, F

from ..models import Enrollment, Lesson


def _lessons_count_for_subjects(subject_ids: Iterable[int]) -> Dict[int, int]:
    """Return mapping of subject_id -> total lessons for given subjects."""

    counts = (
        Lesson.objects.filter(theme__subject_id__in=subject_ids)
        .values("theme__subject_id")
        .annotate(total=Count("id", distinct=True))
    )
    return {row["theme__subject_id"]: row["total"] for row in counts}


def calculate_user_stats(user) -> Dict[str, Any]:
    """Calculate statistics for a particular user.

    The function aggregates information about all enrollments of the user
    and returns data required by the ``/api/lms/stats`` endpoint.
    """

    enrollments = (
        Enrollment.objects.filter(student=user, status__in=["active", "completed"])
        .select_related("subject")
    )

    subject_ids = list(enrollments.values_list("subject_id", flat=True))
    lessons_map = _lessons_count_for_subjects(subject_ids)

    courses = []
    total_courses_enrolled = enrollments.count()
    total_courses_completed = 0
    weighted_sum = 0
    weight_total = 0

    for en in enrollments:
        total = lessons_map.get(en.subject_id, 0)
        completed = int(round((en.progress_percentage or 0) * total / 100))
        percent = int(round(en.progress_percentage or 0))

        if percent >= 100 or en.status == "completed":
            total_courses_completed += 1

        weight = total or 1
        weighted_sum += percent * weight
        weight_total += weight

        courses.append(
            {
                "course_id": en.subject_id,
                "title": en.subject.name,
                "lessons_total": total,
                "lessons_required": total,
                "lessons_completed": completed,
                "percent": percent,
                "started_at": en.enrollment_date,
                "completed_at": en.completion_date,
            }
        )

    overall_percent = int(round(weighted_sum / weight_total)) if weight_total else 0

    return {
        "total_courses_enrolled": total_courses_enrolled,
        "total_courses_completed": total_courses_completed,
        "overall_percent": overall_percent,
        "courses": courses,
    }


# ---------------------------------------------------------------------------
# Legacy placeholder
# ---------------------------------------------------------------------------


def get_user_overview(user, category_id=None) -> Dict[str, Any]:
    """Return aggregated LMS stats for the given user.

    This helper is used by some existing views.  The implementation keeps a
    backward compatible placeholder and does **not** attempt to provide full
    statistics.  New code should rely on :func:`calculate_user_stats` instead.
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
