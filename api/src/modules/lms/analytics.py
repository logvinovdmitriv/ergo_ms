from datetime import date, timedelta
from typing import Optional, Dict, Any, List

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Avg, Q, F
from django.utils import timezone

from .models import (
    Subject,
    Enrollment,
    Grade,
    Test,
    TestAttempt,
    Assignment,
    SubmittedAssignment,
    Forum,
    ForumPost,
    UserBadge,
    Badge,
)


def _parse_date(param: Optional[str], default: date) -> date:
    """Безопасное преобразование строки в дату."""
    if param:
        try:
            return date.fromisoformat(param)
        except ValueError:
            pass
    return default


def get_student_dashboard(
    user: User,
    date_from: Optional[str],
    date_to: Optional[str],
    course_id: Optional[int],
) -> Dict[str, Any]:
    today = timezone.now().date()
    end = _parse_date(date_to, today)
    start = _parse_date(date_from, end - timedelta(days=30))

    enrollments = Enrollment.objects.filter(student=user)
    if course_id:
        enrollments = enrollments.filter(subject_id=course_id)

    in_progress = enrollments.filter(status='active').count()
    completed = enrollments.filter(status='completed').count()

    grades_qs = Grade.objects.filter(student=user, lastupdate__date__range=(start, end))
    if course_id:
        grades_qs = grades_qs.filter(subject_id=course_id)
    gpa = grades_qs.aggregate(avg=Avg('grade'))['avg']

    # просроченные задания
    assignments = Assignment.objects.filter(
        Q(subject__enrollment__student=user)
    )
    if course_id:
        assignments = assignments.filter(subject_id=course_id)

    overdue_tasks = assignments.filter(
        deadline__lt=today
    ).exclude(
        submittedassignment__student=user
    ).count()

    # streak - здесь нет данных, возвращаем 0
    streak_days = 0

    summary = {
        "in_progress": in_progress,
        "completed": completed,
        "gpa": gpa if gpa is not None else None,
        "overdue_tasks": overdue_tasks,
        "streak_days": streak_days,
    }

    grade_trend = [
        {
            "date": rec["lastupdate__date"].isoformat(),
            "avg_grade": rec["avg"],
        }
        for rec in grades_qs.values("lastupdate__date")
        .annotate(avg=Avg("grade"))
        .order_by("lastupdate__date")
    ]

    upcoming_deadlines_qs = assignments.filter(deadline__gte=today).order_by("deadline")
    upcoming_deadlines = []
    for ass in upcoming_deadlines_qs[:10]:
        status = "ok"
        if ass.deadline < today:
            status = "overdue"
        elif ass.deadline <= today + timedelta(days=2):
            status = "risk"
        upcoming_deadlines.append(
            {
                "id": ass.id,
                "title": ass.title,
                "course": {
                    "id": ass.subject.id if ass.subject else None,
                    "name": ass.subject.name if ass.subject else "",
                },
                "due": ass.deadline.isoformat() if ass.deadline else None,
                "status": status,
            }
        )

    # прогресс достижений
    achievements_progress = get_achievements_progress(user.id)

    # рекомендации – пока пусто
    recommendations: List[Dict[str, Any]] = []

    return {
        "summary": summary,
        "grade_trend": grade_trend,
        "upcoming_deadlines": upcoming_deadlines,
        "achievements_progress": achievements_progress,
        "recommendations": recommendations,
    }


def get_teacher_dashboard(
    user: User,
    date_from: Optional[str],
    date_to: Optional[str],
    course_id: Optional[int],
) -> Dict[str, Any]:
    today = timezone.now().date()
    end = _parse_date(date_to, today)
    start = _parse_date(date_from, end - timedelta(days=30))

    courses = Subject.objects.all()
    if not user.is_staff:
        courses = courses.filter(teacher=user)
    if course_id:
        courses = courses.filter(id=course_id)

    enrollments = Enrollment.objects.filter(subject__in=courses)
    total_enrolled = enrollments.count()
    completed = enrollments.filter(status='completed').count()

    completion_rate = (completed / total_enrolled * 100) if total_enrolled else 0

    grades_qs = Grade.objects.filter(subject__in=courses, lastupdate__date__range=(start, end))
    avg_grade = grades_qs.aggregate(avg=Avg('grade'))['avg']

    pending_reviews = SubmittedAssignment.objects.filter(
        assignment__subject__in=courses, grade=0
    ).count()

    summary = {
        "active_courses": courses.count(),
        "enrolled": total_enrolled,
        "completion_rate": completion_rate,
        "on_time_rate": 0.0,
        "avg_grade": avg_grade if avg_grade is not None else None,
        "pending_reviews": pending_reviews,
    }

    course_stats: List[Dict[str, Any]] = []
    for course in courses:
        course_enrollments = enrollments.filter(subject=course)
        c_total = course_enrollments.count()
        c_completed = course_enrollments.filter(status='completed').count()
        c_completion_rate = (c_completed / c_total * 100) if c_total else 0
        c_avg_grade = grades_qs.filter(subject=course).aggregate(avg=Avg('grade'))['avg']
        overdues = Assignment.objects.filter(subject=course, deadline__lt=today).count()
        course_stats.append(
            {
                "id": course.id,
                "name": course.name,
                "enrolled": c_total,
                "completion_rate": c_completion_rate,
                "avg_grade": c_avg_grade if c_avg_grade is not None else None,
                "on_time_rate": 0.0,
                "overdues": overdues,
            }
        )

    distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for value in grades_qs.values_list("grade", flat=True):
        if value >= 90:
            distribution["A"] += 1
        elif value >= 75:
            distribution["B"] += 1
        elif value >= 60:
            distribution["C"] += 1
        elif value >= 50:
            distribution["D"] += 1
        else:
            distribution["F"] += 1

    at_risk_students: List[Dict[str, Any]] = []
    for enr in enrollments.select_related('student', 'subject'):
        overdue = Assignment.objects.filter(
            subject=enr.subject,
            deadline__lt=today
        ).exclude(
            submittedassignment__student=enr.student
        ).count()
        if overdue:
            last_grade = Grade.objects.filter(student=enr.student).order_by('-lastupdate').values_list('lastupdate', flat=True).first()
            at_risk_students.append(
                {
                    "user_id": enr.student.id,
                    "full_name": enr.student.get_full_name() or enr.student.username,
                    "course": {"id": enr.subject.id, "name": enr.subject.name},
                    "overdues": overdue,
                    "last_activity": last_grade.isoformat() if last_grade else None,
                }
            )

    return {
        "summary": summary,
        "courses": course_stats,
        "grade_distribution": distribution,
        "at_risk_students": at_risk_students,
    }


def get_achievements_progress(user_id: int) -> List[Dict[str, Any]]:
    user_badges = set(
        UserBadge.objects.filter(user_id=user_id).values_list("badge_id", flat=True)
    )
    result: List[Dict[str, Any]] = []
    for badge in Badge.objects.filter(is_active=True):
        unlocked = badge.id in user_badges
        result.append(
            {
                "badge_id": badge.id,
                "title": badge.name,
                "category": badge.badge_type,
                "progress": 100 if unlocked else 0,
                "next_threshold": 0 if unlocked else 1,
                "icon": badge.image.url if badge.image else "",
                "unlocked": unlocked,
            }
        )
    return result

class AnalyticsService:
    """Сервис для аналитики и статистики"""
    
    @staticmethod
    def get_student_stats(user: User) -> Dict[str, Any]:
        """Получить статистику студента"""
        # Курсы
        enrolled_courses = Enrollment.objects.filter(student=user, status='active').count()
        completed_courses = Enrollment.objects.filter(student=user, status='completed').count()
        
        # Оценки
        grades = Grade.objects.filter(student=user)
        average_grade = grades.aggregate(models.Avg('grade'))['grade__avg'] or 0
        
        # Тесты
        test_attempts = TestAttempt.objects.filter(student=user)
        total_tests = test_attempts.count()
        passed_tests = test_attempts.filter(is_passed=True).count()
        
        # Задания
        submitted_assignments = SubmittedAssignment.objects.filter(student=user).count()
        
        # Значки и активность
        total_badges = UserBadge.objects.filter(user=user).count()
        forum_posts = ForumPost.objects.filter(author=user).count()
        
        return {
            'enrolled_courses': enrolled_courses,
            'completed_courses': completed_courses,
            'average_grade': round(average_grade, 2),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'submitted_assignments': submitted_assignments,
            'total_badges': total_badges,
            'forum_posts': forum_posts
        }
    
    @staticmethod
    def get_teacher_stats(user: User) -> Dict[str, Any]:
        """Получить статистику преподавателя"""
        subjects = Subject.objects.filter(teacher=user)
        
        # Студенты
        total_students = Enrollment.objects.filter(
            subject__in=subjects, status='active'
        ).values('student').distinct().count()
        
        # Средние оценки
        average_grades = Grade.objects.filter(
            subject__in=subjects
        ).aggregate(models.Avg('grade'))['grade__avg'] or 0
        
        # Активные тесты
        active_tests = Test.objects.filter(
            lesson__theme__subject__in=subjects, is_active=True
        ).count()
        
        # Задания на проверке
        pending_assignments = SubmittedAssignment.objects.filter(
            assignment__lesson__theme__subject__in=subjects, grade=0
        ).count()
        
        # Форумы
        forum_discussions = Forum.objects.filter(subject__in=subjects).count()
        
        # Выданные значки
        badges_awarded = UserBadge.objects.filter(
            badge__subject__in=subjects
        ).count()
        
        return {
            'total_students': total_students,
            'total_subjects': subjects.count(),
            'average_grades': round(average_grades, 2),
            'active_tests': active_tests,
            'pending_assignments': pending_assignments,
            'forum_discussions': forum_discussions,
            'badges_awarded': badges_awarded
        }
    
    @staticmethod
    def get_course_analytics(subject: Subject) -> Dict[str, Any]:
        """Получить аналитику по курсу"""
        enrollments = Enrollment.objects.filter(subject=subject)
        active_count = enrollments.filter(status='active').count()
        completed_count = enrollments.filter(status='completed').count()
        
        # Оценки
        grades = Grade.objects.filter(subject=subject)
        avg_grade = grades.aggregate(models.Avg('grade'))['grade__avg'] or 0
        
        # Прогресс
        avg_progress = enrollments.aggregate(
            models.Avg('progress_percentage')
        )['progress_percentage__avg'] or 0
        
        return {
            'active_students': active_count,
            'completed_students': completed_count,
            'average_grade': round(avg_grade, 2),
            'average_progress': round(avg_progress, 2),
            'completion_rate': round(
                (completed_count / (active_count + completed_count) * 100) 
                if (active_count + completed_count) > 0 else 0, 2
            )
        }


class ReportsService:
    """Сервис для генерации детальных отчетов"""
    
    @staticmethod
    def generate_performance_report(subject: Subject) -> Dict[str, Any]:
        """Генерация отчета по успеваемости курса"""
        students = Enrollment.objects.filter(
            subject=subject, status='active'
        ).select_related('student')
        
        report = []
        for enrollment in students:
            student = enrollment.student
            student_grades = Grade.objects.filter(
                student=student, subject=subject
            )
            avg_grade = student_grades.aggregate(
                models.Avg('grade')
            )['grade__avg'] or 0
            
            test_attempts = TestAttempt.objects.filter(
                student=student,
                test__lesson__theme__subject=subject
            )
            avg_test_score = test_attempts.aggregate(
                models.Avg('score')
            )['score__avg'] or 0
            
            report.append({
                'student_name': student.get_full_name() or student.username,
                'average_grade': round(avg_grade, 2),
                'average_test_score': round(avg_test_score, 2),
                'progress': enrollment.progress_percentage,
                'last_activity': enrollment.enrollment_date  # можно заменить на реальную активность
            })
        
        return {
            'subject': subject.name,
            'total_students': len(report),
            'students': report
        } 